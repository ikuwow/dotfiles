#!/usr/bin/env python3
"""Auto-approve commands that don't have command substitution outside single quotes.

Background:
  Claude Code's security pre-checks flag commands containing backticks,
  $(), heredocs, and multiline strings — even when they appear inside
  single-quoted strings where the shell will NOT expand them.

  The pre-checks run BEFORE allow/deny rule matching and override the
  allow list (see https://github.com/anthropics/claude-code/issues/11932).

  This hook fires via the PermissionRequest event (just before the
  approval prompt is shown) and auto-approves commands that are safe:
  command substitution ($() or backticks) is only dangerous when it
  appears OUTSIDE single-quoted strings.

Spec: https://docs.anthropic.com/en/docs/claude-code/hooks
"""
import json
import sys

APPROVED_PREFIXES = (
    "git commit",
    "gh pr create",
    "gh issue create",
)


def has_unsafe_substitution(command: str) -> bool:
    """Check if command has $() or backticks outside single-quoted strings.

    Shell single-quoting rules: everything between '...' is literal.
    Split by ' to determine inside vs outside. Even-indexed segments
    are outside single quotes, odd-indexed are inside.

    Safe (substitution inside single quotes):
    >>> has_unsafe_substitution("git commit -m 'msg with `code`'")
    False
    >>> has_unsafe_substitution("git commit -m 'msg with $(foo)'")
    False
    >>> has_unsafe_substitution("gh pr create --body '## `Title`\\n$(not expanded)'")
    False

    Unsafe (substitution outside single quotes):
    >>> has_unsafe_substitution("git commit -m \\"$(cat file)\\"")
    True
    >>> has_unsafe_substitution("git commit -m \\"`date`\\"")
    True
    >>> has_unsafe_substitution("git commit -m $(cat file)")
    True

    No substitution at all:
    >>> has_unsafe_substitution("git commit -m 'simple message'")
    False
    >>> has_unsafe_substitution("git commit --amend")
    False
    """
    parts = command.split("'")
    for i, part in enumerate(parts):
        if i % 2 == 0:  # outside single quotes
            if "$(" in part or "`" in part:
                return True
    return False


def should_approve(tool_name: str, command: str) -> bool:
    """Return True if the permission request should be auto-approved.

    >>> should_approve("Bash", "git commit -m 'fix: resolve `encoding` issue'")
    True
    >>> should_approve("Bash", "gh pr create --draft --title 'title' --body '## Summary\\n`code`'")
    True
    >>> should_approve("Bash", "gh issue create --title 'title' --body 'body'")
    True
    >>> should_approve("Bash", "git commit -m \\"$(evil)\\"")
    False
    >>> should_approve("Bash", "git push origin main")
    False
    >>> should_approve("Edit", "git commit -m 'wrong tool'")
    False
    """
    if tool_name != "Bash":
        return False
    stripped = command.lstrip()
    if not stripped.startswith(APPROVED_PREFIXES):
        return False
    if has_unsafe_substitution(stripped):
        return False
    return True


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if should_approve(
        data.get("tool_name", ""),
        data.get("tool_input", {}).get("command", ""),
    ):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "allow"}
            }
        }))

    sys.exit(0)
