#!/usr/bin/env python3
"""Block Bash commands that chain ``cd`` with other commands.

Chaining ``cd`` with ``&&``, ``;``, or ``||`` is prohibited because:
  - It bypasses bare-repository-attack prevention checks.
  - Combined commands don't match individual allow-list patterns,
    causing unnecessary permission prompts.

This PreToolUse hook inspects Bash tool calls and blocks any command
where ``cd`` appears as a segment in a multi-segment command
(separated by ``&&``, ``||``, or ``;`` outside of quotes).

Spec: https://docs.anthropic.com/en/docs/claude-code/hooks
"""
import json
import re
import sys

# Matches shell separators: &&, ||, ;, newline
_SEPARATOR_RE = re.compile(r"&&|\|\||;|\n")

# Matches "cd" followed by whitespace or end of string
_CD_RE = re.compile(r"^cd(\s|$)")


def _split_outside_quotes(command: str) -> list[str]:
    """Split command by shell separators, ignoring separators inside quotes.

    >>> _split_outside_quotes("cd /path && ls")
    ['cd /path ', ' ls']
    >>> _split_outside_quotes("echo 'cd /path && ls'")
    ["echo 'cd /path && ls'"]
    >>> _split_outside_quotes('echo "cd /path && ls"')
    ['echo "cd /path && ls"']
    >>> _split_outside_quotes("cd /path ; echo 'hello ; world' && pwd")
    ['cd /path ', " echo 'hello ; world' ", ' pwd']
    >>> _split_outside_quotes('echo "a\\\\" && cd /x"')
    ['echo "a\\\\" && cd /x"']
    >>> _split_outside_quotes("cd /path\\ngit status")
    ['cd /path', 'git status']
    """
    segments = []
    current = []
    in_single = False
    in_double = False
    i = 0
    while i < len(command):
        ch = command[i]

        # Handle backslash escapes inside double quotes
        if ch == "\\" and in_double and i + 1 < len(command):
            current.append(ch)
            current.append(command[i + 1])
            i += 2
            continue

        # Toggle quote state
        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
            i += 1
            continue

        # Check for separators only outside quotes
        if not in_single and not in_double:
            match = _SEPARATOR_RE.match(command, i)
            if match:
                segments.append("".join(current))
                current = []
                i = match.end()
                continue

        current.append(ch)
        i += 1

    segments.append("".join(current))
    return segments


def has_chained_cd(command: str) -> bool:
    """Return True if ``cd`` is chained with other commands.

    Blocked (cd chained with other commands):
    >>> has_chained_cd("cd /some/path && terraform plan")
    True
    >>> has_chained_cd("cd /path ; ls -la")
    True
    >>> has_chained_cd("cd /path || echo failed")
    True
    >>> has_chained_cd("ls && cd /path")
    True
    >>> has_chained_cd("cd /a && cd /b")
    True

    Allowed (cd alone):
    >>> has_chained_cd("cd /some/path")
    False
    >>> has_chained_cd("cd .worktrees/feature")
    False

    Allowed (cd only inside quotes, not a real segment):
    >>> has_chained_cd("echo 'cd /path && foo'")
    False
    >>> has_chained_cd("git commit -m 'cd somewhere ; do stuff'")
    False

    Allowed (no cd at all):
    >>> has_chained_cd("ls && pwd")
    False
    >>> has_chained_cd("terraform plan")
    False

    Blocked (cd with tab separator):
    >>> has_chained_cd("cd\\t/path && ls")
    True

    Blocked (cd with newline separator):
    >>> has_chained_cd("cd /path\\ngit status")
    True
    >>> has_chained_cd("cd /path\\ncd /other")
    True
    >>> has_chained_cd("ls -la\\ncd /path")
    True

    Allowed (newline inside quotes):
    >>> has_chained_cd("echo 'cd /path\\ngit status'")
    False
    """
    segments = _split_outside_quotes(command)
    if len(segments) < 2:
        return False
    return any(_CD_RE.match(seg.strip()) for seg in segments)


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    command = data.get("tool_input", {}).get("command", "")

    if tool_name == "Bash" and has_chained_cd(command):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Do not chain `cd` with other commands using &&, ;, ||, "
                    "or newlines. Run `cd` as a separate Bash call first, "
                    "then run the other command in the next call."
                ),
            },
        }))

    sys.exit(0)
