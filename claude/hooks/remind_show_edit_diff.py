#!/usr/bin/env python3
"""Remind the agent to show a diff after editing a PR/issue title or body.

Fires on ``PostToolUse`` events for ``Bash`` calls. When the command is a
``gh pr edit`` or ``gh issue edit`` invocation that includes a flag which
overwrites the title or body (``--title``/``-t``, ``--body``/``-b``, or
``--body-file``/``-F``), emits an ``additionalContext`` reminder to present
the before/after diff to the user, since these flags silently replace the
existing content and a mistaken value is otherwise easy to lose. No state is
persisted; the reminder fires on every matching command in every session by
design.

Registered under ``PostToolUse`` with ``matcher: "Bash"``. Set
``ENABLE_EDIT_DIFF_REMINDER=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#posttooluse
"""
import json
import os
import re
import shlex
import sys

_EDIT_FLAGS = {"--title", "-t", "--body", "-b", "--body-file", "-F"}

MESSAGE = (
    "A `gh pr edit` / `gh issue edit` that changed the title or body just "
    "ran. If you did not present the before/after diff to the user before "
    "executing this, present it now: fetch the previous value (from the "
    "earlier `gh pr view` / `gh issue view` output already in this "
    "conversation, or by re-fetching if you cannot recover it) and show a "
    "diff against the new body you just applied. This gives the user a "
    "chance to catch and recover overwritten content. See the git-workflow "
    "skill Section 5 for the canonical pre-edit procedure."
)


def _is_edit_diff_command(command: str) -> bool:
    normalized = re.sub(r"\s+", " ", command).strip()
    if "gh pr edit " not in normalized and "gh issue edit " not in normalized:
        return False
    try:
        tokens = shlex.split(normalized)
    except ValueError:
        # Unbalanced quotes or similar: don't guess, fail open silently.
        return False
    return any(token in _EDIT_FLAGS for token in tokens)


def main() -> None:
    if os.environ.get("ENABLE_EDIT_DIFF_REMINDER", "1") == "0":
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    if not isinstance(data, dict):
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)

    command = (data.get("tool_input") or {}).get("command", "")
    if not command:
        sys.exit(0)

    if not _is_edit_diff_command(command):
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": MESSAGE,
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
