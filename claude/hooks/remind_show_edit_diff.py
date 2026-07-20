#!/usr/bin/env python3
"""Remind the agent to show a diff after editing a PR/issue title or body.

Fires on ``PostToolUse`` events for ``Bash`` calls. When the command begins
with ``gh pr edit`` or ``gh issue edit`` and includes a flag that overwrites
the title or body (``--title``/``-t``, ``--body``/``-b``, ``--body-file``/
``-F``, and the ``=``-joined forms of the long options), emits an
``additionalContext`` reminder to present the before/after diff to the user.
The reminder is only actionable when the prior value is still visible in
the conversation (an earlier ``gh {pr,issue} view`` output, or the body file
the agent wrote): re-fetching after the edit returns the new value, so a
lost prior value cannot be reconstructed from the server.

The command must actually start with ``gh (pr|issue) edit`` (first three
tokens), so short flags like ``-F`` appearing in compound commands
(``... && grep -F pat``) do not over-fire. No state is persisted; the
reminder fires on every matching command in every session by design.

Registered under ``PostToolUse`` with ``matcher: "Bash"``. Set
``ENABLE_EDIT_DIFF_REMINDER=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#posttooluse
"""
import json
import os
import shlex
import sys

_EDIT_FLAGS = frozenset({"--title", "-t", "--body", "-b", "--body-file", "-F"})
_SHELL_OPERATORS = frozenset({"&&", "||", "|", ";", "&", "\n"})

MESSAGE = (
    "A `gh pr edit` / `gh issue edit` that changed the title or body just "
    "ran. If you did not present the before/after diff to the user before "
    "executing this, present it now using the prior value from earlier in "
    "this conversation (an earlier `gh pr view` / `gh issue view` output, "
    "or the body file you wrote for this edit). Re-fetching now returns "
    "the new value, so recovery is only possible when the prior value is "
    "still visible in context. For future edits, follow the `Update a PR "
    "/ issue` procedure in the git-workflow skill so the diff is shown "
    "before the edit runs."
)


def _matches_edit_flag(token: str) -> bool:
    """Match ``--title``, ``-t``, etc. and their ``--flag=value`` forms.

    >>> _matches_edit_flag("--title")
    True
    >>> _matches_edit_flag("--title=NEW")
    True
    >>> _matches_edit_flag("-t")
    True
    >>> _matches_edit_flag("--body-file=/tmp/x")
    True
    >>> _matches_edit_flag("--add-label")
    False
    >>> _matches_edit_flag("--titles")
    False
    """
    return token.split("=", 1)[0] in _EDIT_FLAGS


def _is_edit_diff_command(command: str) -> bool:
    """Return True when the command runs ``gh (pr|issue) edit`` with an overwrite flag.

    >>> _is_edit_diff_command("gh pr edit 123 --body-file /tmp/x")
    True
    >>> _is_edit_diff_command("gh issue edit 5 --title='new title'")
    True
    >>> _is_edit_diff_command("gh pr edit 123 --add-label foo")
    False
    >>> _is_edit_diff_command("gh pr create --body-file /tmp/x")
    False
    >>> _is_edit_diff_command("gh pr edit 123 --add-label foo && grep -F pat log")
    False
    >>> _is_edit_diff_command("gh pr edit 123 -t 'new'")
    True
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if len(tokens) < 4:
        return False
    if tokens[0] != "gh" or tokens[1] not in ("pr", "issue") or tokens[2] != "edit":
        return False
    for tok in tokens[3:]:
        if tok in _SHELL_OPERATORS:
            break
        if _matches_edit_flag(tok):
            return True
    return False


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

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        sys.exit(0)
    command = tool_input.get("command", "")
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
