"""Shared utilities for Claude Code PermissionRequest hooks.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import sys


def has_unsafe_substitution(command: str) -> bool:
    """Check if command has $() or backticks outside single-quoted strings.

    Uses a state machine to track single/double quote context. Only
    single quotes suppress command substitution in shell; double quotes
    do NOT prevent $() or backtick expansion. Handles backslash escapes
    inside double quotes and the shell idiom '\\'' (end single-quote,
    literal escaped quote, start single-quote).

    Safe (substitution inside single quotes):
    >>> has_unsafe_substitution("git commit -m 'msg with `code`'")
    False
    >>> has_unsafe_substitution("git commit -m 'msg with $(foo)'")
    False
    >>> has_unsafe_substitution("gh pr create --body '## `Title`\\n$(not expanded)'")
    False

    Safe (shell-escaped single quote — '\\'' idiom):
    >>> has_unsafe_substitution("git commit -m 'don'\\\\''t do $(this)'")
    False

    Unsafe (substitution inside double quotes — shell expands these):
    >>> has_unsafe_substitution("git commit -m \\"$(cat file)\\"")
    True
    >>> has_unsafe_substitution("git commit -m \\"`date`\\"")
    True

    Unsafe (substitution outside all quotes):
    >>> has_unsafe_substitution("git commit -m $(cat file)")
    True

    Unsafe (breaking out of single quotes):
    >>> has_unsafe_substitution("git commit -m 'safe'$(evil)'rest'")
    True

    No substitution at all:
    >>> has_unsafe_substitution("git commit -m 'simple message'")
    False
    >>> has_unsafe_substitution("git commit --amend")
    False
    """
    in_single = False
    in_double = False
    i = 0
    while i < len(command):
        ch = command[i]

        # Backslash escapes: skip next char when outside single quotes
        # (inside single quotes, backslash is literal in shell)
        if ch == "\\" and not in_single and i + 1 < len(command):
            i += 2
            continue

        # Toggle quote state
        if ch == "'" and not in_double:
            in_single = not in_single
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            i += 1
            continue

        # Only single quotes suppress substitution; double quotes do NOT
        if not in_single:
            if ch == "$" and i + 1 < len(command) and command[i + 1] == "(":
                return True
            if ch == "`":
                return True

        i += 1
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
