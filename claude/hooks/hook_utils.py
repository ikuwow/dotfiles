"""Shared utilities for Claude Code PermissionRequest hooks.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import sys


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


def approve_and_exit():
    """Print the JSON approval decision and exit."""
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "allow"}
        }
    }))
    sys.exit(0)


def read_hook_input():
    """Read and parse JSON from stdin. Returns (tool_name, command).

    Returns empty strings on parse failure.
    """
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return "", ""
    return (
        data.get("tool_name", ""),
        data.get("tool_input", {}).get("command", ""),
    )
