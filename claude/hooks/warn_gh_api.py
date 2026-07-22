#!/usr/bin/env python3
"""Handle gh api permission requests: auto-allow reads, soft-deny mutations.

Fires on ``PermissionRequest`` events (when a permission dialog would
appear for a ``gh api`` call). Splits behavior by whether the call
mutates state:

- Read-only shape (no ``--method``/``-X`` other than GET, no body
  flags ``--input``/``-f``/``-F``/``--field``/``--raw-field``):
  emits ``allow`` so the dialog does not appear and no soft-deny
  round-trip is spent. State is not touched.
- Mutation shape: on the first occurrence of each distinct command
  per session, denies with a "prefer high-level gh subcommands"
  message so the assistant reconsiders before the user is prompted.
  Re-issuing the same command in the same session lets the hook
  fall through (``exit 0``) so the dialog reaches the user and they
  can approve. Two commands are considered the same when they match
  after whitespace normalization (leading/trailing trim, internal
  runs of whitespace collapsed to a single space).

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
import shlex
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


def _save_state(session_id: str, shown: set) -> bool:
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
        with open(_state_path(session_id), "w") as f:
            json.dump(sorted(shown), f)
    except OSError:
        return False
    return True


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


_BODY_FLAGS = frozenset({"--input", "-f", "-F", "--field", "--raw-field"})


def _is_mutation(command: str) -> bool:
    """Return True if a gh api command mutates state.

    Read-only shape has no body flags and either no method flag or an
    explicit GET method. Any other method (POST/PATCH/PUT/DELETE) is a
    mutation. Body flags (``-f``, ``-F``, ``--field``, ``--raw-field``,
    ``--input``) imply a POST-like request body regardless of method.

    On parse failure (unbalanced quotes etc.) returns True so the
    conservative soft-deny path stays engaged.

    >>> _is_mutation("gh api /repos/owner/repo/pulls/1/comments")
    False
    >>> _is_mutation("gh api /repos/owner/repo/pulls/1 --method PATCH -f title=foo")
    True
    >>> _is_mutation("gh api /repos/owner/repo/pulls/1 -X GET")
    False
    >>> _is_mutation("gh api /repos/owner/repo/pulls/1 --method=GET")
    False
    >>> _is_mutation("gh api /repos/owner/repo/pulls/1 --method=POST")
    True
    >>> _is_mutation("gh api graphql -f query='{ viewer { login } }'")
    True
    >>> _is_mutation("gh api /repos/owner/repo/pulls/1 -X POST")
    True
    >>> _is_mutation("gh api /repos/owner/repo -X get")
    False
    >>> _is_mutation("gh api /repos/owner/repo --raw-field body=@-")
    True
    >>> _is_mutation("gh api /repos/owner/repo --field name=value")
    True
    >>> _is_mutation("gh api /repos/owner/repo --input payload.json")
    True
    >>> _is_mutation("gh api /repos/owner/repo -XPATCH")
    True
    >>> _is_mutation("gh api /repos/owner/repo -XGET")
    False
    >>> _is_mutation("gh api /repos/owner/repo -Xpost")
    True
    >>> _is_mutation("gh api /repos/owner/repo -fkey=value")
    True
    >>> _is_mutation("gh api /repos/owner/repo -Fkey=@file")
    True
    >>> _is_mutation("gh api /repos/owner/repo --method")
    True
    >>> _is_mutation("gh api 'unterminated quote")
    True
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return True

    try:
        idx = next(i for i, t in enumerate(tokens) if t == "api" and i > 0 and tokens[i - 1] == "gh")
    except StopIteration:
        return True

    args = tokens[idx + 1:]
    i = 0
    while i < len(args):
        arg = args[i]

        # Glued short forms (pflag accepts -XPOST, -fkey=value, -Fkey=value).
        if len(arg) > 2 and arg.startswith("-X") and arg[2] != "=":
            if arg[2:].upper() != "GET":
                return True
            i += 1
            continue
        if len(arg) > 2 and (arg.startswith("-f") or arg.startswith("-F")) and arg[2] != "=":
            return True

        if arg in _BODY_FLAGS:
            return True
        if "=" in arg:
            flag, _, value = arg.partition("=")
            if flag in _BODY_FLAGS:
                return True
            if flag in ("--method", "-X"):
                if value.upper() != "GET":
                    return True
                i += 1
                continue
        if arg in ("--method", "-X"):
            if i + 1 >= len(args):
                return True
            if args[i + 1].upper() != "GET":
                return True
            i += 2
            continue
        i += 1
    return False


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

    command = (data.get("tool_input") or {}).get("command", "")
    if not command:
        sys.exit(0)

    # Belt-and-suspenders against the settings.json `if` filter failing open
    # on parse errors or matching subshell-only occurrences.
    if "gh api" not in command:
        sys.exit(0)

    if not _is_mutation(command):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": "allow",
                },
            },
        }))
        sys.exit(0)

    session_id = data.get("session_id", "default")
    shown = _load_state(session_id)
    key = _command_key(command)

    if key not in shown:
        shown.add(key)
        if not _save_state(session_id, shown):
            # State didn't persist; skip the deny so the retry isn't
            # infinite. Permission dialog reaches the user this time.
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

    sys.exit(0)


if __name__ == "__main__":
    main()
