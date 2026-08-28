"""Shared utilities for Claude Code hooks.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import re
import sys

_SEPARATOR_RE = re.compile(r"&&|\|\||;|\||&|\n")


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


def split_outside_quotes(command: str) -> list[str]:
    """Split by shell separators (&&, ||, ;, |, &, newline), ignoring separators inside quotes.

    Bash line continuation ``\\`` + newline outside quotes is collapsed
    before splitting so a multi-line command still lands in one segment.

    >>> split_outside_quotes("aws logs start-query | jq .")
    ['aws logs start-query ', ' jq .']
    >>> split_outside_quotes("echo 'aws logs start-query | jq .'")
    ["echo 'aws logs start-query | jq .'"]
    >>> split_outside_quotes("foo && aws logs start-query")
    ['foo ', ' aws logs start-query']
    >>> split_outside_quotes("aws logs start-query \\\\\\n  --foo bar")
    ['aws logs start-query   --foo bar']
    """
    segments: list[str] = []
    current: list[str] = []
    in_single = in_double = False
    i = 0
    while i < len(command):
        ch = command[i]
        if ch == "\\" and not in_single and i + 1 < len(command) and command[i + 1] == "\n":
            i += 2
            continue
        if ch == "\\" and in_double and i + 1 < len(command):
            current.append(ch)
            current.append(command[i + 1])
            i += 2
            continue
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
        if not in_single and not in_double:
            m = _SEPARATOR_RE.match(command, i)
            if m:
                segments.append("".join(current))
                current = []
                i = m.end()
                continue
        current.append(ch)
        i += 1
    segments.append("".join(current))
    return segments


def collect_current_turn_blocks(events):
    """Collect raw assistant content blocks emitted since the last real user message.

    Walks events backward and stops at a real user message; user events
    whose content is purely tool_result blocks are tool-call re-entries,
    not turn boundaries, and are skipped. Returns every content block
    (text, tool_use, etc.), events walked from most recent to least
    recent, but blocks within one assistant message kept in their
    original emission order — a caller that needs only text filters
    for block.get("type") == "text".

    Single-turn capture, both a text and a tool_use block:

    >>> events = [
    ...     {"type": "user", "message": {"role": "user", "content": "hi"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "on it"},
    ...         {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
    ...     ]}},
    ... ]
    >>> collect_current_turn_blocks(events) == [
    ...     {"type": "text", "text": "on it"},
    ...     {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
    ... ]
    True

    Tool-call re-entry does not end the turn; both text blocks are
    captured (in reverse-walk order):

    >>> events = [
    ...     {"type": "user", "message": {"role": "user", "content": "x"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "first"}
    ...     ]}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "tool_use", "name": "Bash"}
    ...     ]}},
    ...     {"type": "user", "message": {"role": "user", "content": [
    ...         {"type": "tool_result", "content": "ok"}
    ...     ]}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "second"}
    ...     ]}},
    ... ]
    >>> [b.get("text") for b in collect_current_turn_blocks(events) if b.get("type") == "text"]
    ['second', 'first']

    A real user message ends the scan; older turns are not captured:

    >>> events = [
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "old"}
    ...     ]}},
    ...     {"type": "user", "message": {"role": "user", "content": "new turn"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "current"}
    ...     ]}},
    ... ]
    >>> [b.get("text") for b in collect_current_turn_blocks(events) if b.get("type") == "text"]
    ['current']

    Mixed content (a tool_result alongside a real content block) is a
    genuine turn boundary, not a re-entry — the boundary check requires
    *every* block in the user message to be a tool_result, not merely
    *any* of them, so blocks from the turn before the boundary are not
    swept in:

    >>> events = [
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "old"}
    ...     ]}},
    ...     {"type": "user", "message": {"content": [
    ...         {"type": "tool_result", "content": "ok"},
    ...         {"type": "text", "text": "also human text"},
    ...     ]}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "reply"}
    ...     ]}},
    ... ]
    >>> [b.get("text") for b in collect_current_turn_blocks(events) if b.get("type") == "text"]
    ['reply']

    Empty input:

    >>> collect_current_turn_blocks([])
    []

    Malformed events are skipped silently — system events, non-dict
    JSONL lines, assistant messages with missing or null content,
    user events with a null message, etc. A `.get` default does not
    fire on an explicit null, so each shape is checked explicitly
    rather than trusting a default to catch it:

    >>> events = [
    ...     {"type": "system"},
    ...     "not a dict",
    ...     {"type": "assistant", "message": {}},
    ...     {"type": "assistant", "message": {"content": None}},
    ...     {"type": "user", "message": None},
    ...     {"type": "user", "message": {"role": "user", "content": "hi"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "ok"}
    ...     ]}},
    ... ]
    >>> [b.get("text") for b in collect_current_turn_blocks(events) if b.get("type") == "text"]
    ['ok']
    """
    blocks = []
    for event in reversed(events):
        if not isinstance(event, dict):
            continue
        if event.get("type") == "user":
            message = event.get("message")
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, str):
                break
            if isinstance(content, list) and not all(
                isinstance(c, dict) and c.get("type") == "tool_result"
                for c in content
            ):
                break
            continue
        if event.get("type") != "assistant":
            continue
        message = event.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        for block in content or []:
            if isinstance(block, dict):
                blocks.append(block)
    return blocks


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
