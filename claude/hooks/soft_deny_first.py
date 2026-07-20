#!/usr/bin/env python3
"""Soft-deny the first occurrence of any dialog-bound tool call.

Fires on ``PermissionRequest`` events (when a permission dialog would
appear for a ``Bash``, ``Edit``, ``Write``, or ``NotebookEdit`` call). On
the first occurrence of each distinct call within a 10-minute window
per session, denies the permission with a message that steers the
agent toward a route that does not need permission, or asks it to
retry the exact same call with its reason stated. Re-issuing the same
call within the TTL lets the hook fall through (``exit 0``) so the
dialog reaches the user and they can approve.

Inert in manual mode (``permission_mode`` absent or ``"default"``):
manual mode is chosen deliberately, so its prompts must appear without
an extra agent round-trip.

Registered under ``PermissionRequest`` with
``matcher: "Bash|Edit|Write|NotebookEdit"``. Defers to
``approve_git_gh_commands.should_approve``: a Bash command that hook
would auto-approve is never denied here, since the allow+deny
combination across sibling hooks is undocumented. Leaves ``gh api``
commands to ``warn_gh_api.py``, which owns that carve-out.

Session state is tracked in
``~/.claude/state/soft_deny_first_<session_id>.json``, with a 10
minute TTL per entry. Set ``ENABLE_SOFT_DENY_FIRST=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#permissionrequest
"""
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime

try:
    from approve_git_gh_commands import should_approve
except Exception:  # fail open if the sibling is missing or broken
    should_approve = None

_STATE_DIR = os.path.expanduser("~/.claude/state")
_STATE_PREFIX = "soft_deny_first_"
_TTL_SECONDS = 600
_TOOLS = ("Bash", "Edit", "Write", "NotebookEdit")

MESSAGE = (
    "Permission would be required for this call. First consider a route "
    "that does not need permission. If no such route exists, retry the "
    "exact same call with your reason stated; the retry will reach the "
    "user for confirmation. (Bash commands match with whitespace "
    "normalized; other tools require identical input; the exemption "
    "lasts 10 minutes.)"
)


def _cache_key(tool_name: str, tool_input: dict) -> str:
    """Return a stable state key for a tool call.

    For Bash, only the whitespace-normalized command is hashed, so a
    retry with a rephrased description or extra whitespace hits the
    same key. For other tools, the whole tool_input is hashed as
    canonical JSON.

    >>> a = _cache_key("Bash", {"command": "curl example.com", "description": "fetch"})
    >>> b = _cache_key("Bash", {"command": "curl  example.com ", "description": "get it"})
    >>> a == b
    True
    >>> c = _cache_key("Write", {"file_path": "/tmp/x", "content": "hi"})
    >>> d = _cache_key("Write", {"content": "hi", "file_path": "/tmp/x"})
    >>> c == d
    True
    >>> _cache_key("Bash", {"command": "ls"}) == _cache_key("Edit", {"command": "ls"})
    False
    """
    if tool_name == "Bash":
        payload = re.sub(r"\s+", " ", tool_input.get("command", "")).strip()
    else:
        payload = json.dumps(tool_input, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{tool_name}\n{payload}".encode("utf-8")).hexdigest()


def _state_path(session_id: str) -> str:
    return os.path.join(_STATE_DIR, f"{_STATE_PREFIX}{session_id}.json")


def _load_state(session_id: str, now: float) -> dict:
    try:
        with open(_state_path(session_id)) as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        key: ts
        for key, ts in data.items()
        if isinstance(ts, (int, float)) and now - ts <= _TTL_SECONDS
    }


def _save_state(session_id: str, entries: dict) -> bool:
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
        path = _state_path(session_id)
        tmp_path = f"{path}.tmp.{os.getpid()}"
        with open(tmp_path, "w") as f:
            json.dump(entries, f)
        os.replace(tmp_path, path)
    except OSError:
        return False
    return True


def _cleanup_old_state() -> None:
    try:
        if not os.path.isdir(_STATE_DIR):
            return
        cutoff = datetime.now().timestamp() - 24 * 60 * 60
        for name in os.listdir(_STATE_DIR):
            if not name.startswith(_STATE_PREFIX) or not name.endswith(".json"):
                continue
            path = os.path.join(_STATE_DIR, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                pass
    except OSError:
        pass


def main() -> None:
    if os.environ.get("ENABLE_SOFT_DENY_FIRST", "1") == "0":
        sys.exit(0)

    if random.random() < 0.1:
        _cleanup_old_state()

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    if not isinstance(data, dict):
        sys.exit(0)

    permission_mode = data.get("permission_mode")
    if not permission_mode:
        # The spec sends this field on PermissionRequest; its absence is
        # unexpected, and skipping here silently disables the hook.
        print("soft_deny_first: permission_mode missing", file=sys.stderr)
        sys.exit(0)
    if permission_mode == "default":
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in _TOOLS:
        sys.exit(0)

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict) or not tool_input:
        sys.exit(0)

    command = tool_input.get("command", "") if tool_name == "Bash" else ""
    if tool_name == "Bash" and "gh api" in command:
        # Owned by warn_gh_api.py; keep the two hooks' boundaries aligned.
        sys.exit(0)

    if tool_name == "Bash":
        # should_approve only ever matters for Bash, so a broken sibling
        # must not disable the hook for the other tools.
        if should_approve is None:
            print("soft_deny_first: approve_git_gh_commands unavailable", file=sys.stderr)
            sys.exit(0)
        if should_approve("Bash", command):
            # approve_git_gh_commands will emit allow in parallel; never deny
            # what it would allow (the allow+deny combination is undocumented).
            sys.exit(0)

    session_id = data.get("session_id", "default")
    now = datetime.now().timestamp()
    entries = _load_state(session_id, now)
    key = _cache_key(tool_name, tool_input)

    if key in entries:
        # Fresh within TTL: let the normal dialog appear, and do not
        # refresh the timestamp.
        sys.exit(0)

    entries[key] = now
    if not _save_state(session_id, entries):
        # State didn't persist; skip the deny so the retry isn't
        # infinite. Permission dialog reaches the user this time.
        print("soft_deny_first: could not persist state", file=sys.stderr)
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {
                "behavior": "deny",
                "message": MESSAGE,
            },
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
