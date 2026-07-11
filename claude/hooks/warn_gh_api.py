#!/usr/bin/env python3
"""Warn on gh api permission requests.

Fires on ``PermissionRequest`` events (when a permission dialog would
appear for a ``gh api`` call). On the first occurrence of each distinct
command per session, denies the permission with a "prefer high-level gh
subcommands" message so the assistant reconsiders before the user is
prompted. Re-issuing the same command in the same session lets the hook
fall through (``exit 0``) so the dialog reaches the user and they can
approve. Two commands are considered the same when they match after
whitespace normalization (leading/trailing trim, internal runs of
whitespace collapsed to a single space).

Registered under ``PermissionRequest`` with ``matcher: "Bash"`` and
``if: "Bash(gh api *)"``. The ``if`` filter narrows to gh api commands,
and the ``PermissionRequest`` lifecycle already excludes commands that
permission ``allow`` rules would run without a dialog — so this hook
only fires when the user was about to see a prompt anyway.

Session state is tracked in ``~/.claude/state/gh_api_warned_<session_id>.json``.
Set ``ENABLE_GH_API_WARNING=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#permissionrequest
"""
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime

_STATE_DIR = os.path.expanduser("~/.claude/state")
_STATE_PREFIX = "gh_api_warned_"

MESSAGE = (
    "Detected 'gh api'. Prefer high-level gh subcommands first:\n"
    "  gh pr view / gh pr diff / gh pr checks\n"
    "  gh issue view (with --comments)\n"
    "  gh run view\n"
    "  gh pr-review (extension: agynio/gh-pr-review) for PR review threads\n"
    "Fall back to 'gh api' / 'gh api graphql' only when the high-level "
    "subcommands cannot express the operation. If that is the case, "
    "re-run the exact same command as-is — this session lets it through "
    "on the second and later occurrences of the same command (matched "
    "with whitespace normalized)."
)


def _state_path(session_id: str) -> str:
    return os.path.join(_STATE_DIR, f"{_STATE_PREFIX}{session_id}.json")


def _load_state(session_id: str) -> set:
    try:
        with open(_state_path(session_id)) as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def _save_state(session_id: str, shown: set) -> None:
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
        with open(_state_path(session_id), "w") as f:
            json.dump(sorted(shown), f)
    except OSError:
        pass


def _cleanup_old_state() -> None:
    try:
        if not os.path.isdir(_STATE_DIR):
            return
        cutoff = datetime.now().timestamp() - 30 * 24 * 60 * 60
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


def _command_key(command: str) -> str:
    """Return a stable state key for a command, normalizing whitespace.

    >>> _command_key("gh api foo") == _command_key("gh  api  foo")
    True
    >>> _command_key("gh api foo") == _command_key(" gh api foo ")
    True
    >>> _command_key("gh api foo") == _command_key("gh api bar")
    False
    """
    normalized = re.sub(r"\s+", " ", command).strip()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def main() -> None:
    if os.environ.get("ENABLE_GH_API_WARNING", "1") == "0":
        sys.exit(0)

    if random.random() < 0.1:
        _cleanup_old_state()

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    session_id = data.get("session_id", "default")
    shown = _load_state(session_id)
    key = _command_key(command)

    if key not in shown:
        shown.add(key)
        _save_state(session_id, shown)
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

    sys.exit(0)


if __name__ == "__main__":
    main()
