#!/usr/bin/env python3
"""Deny curl/wget fetches of raw.githubusercontent.com in favor of ``gh``.

Fetching raw.githubusercontent.com directly is only warranted when
``gh`` itself is unavailable. This PreToolUse hook carries that
constraint: a Bash command that reaches for ``curl``/``wget`` against
that domain is denied and pointed at the ``gh api`` equivalent instead,
with the "ask the user" fallback for the case where ``gh`` cannot run.

The predicate asks for an invocation, not a mention. A command is
denied when ``curl`` or ``wget`` stands at the head of a segment
(splitting on ``&&``, ``||``, ``;``, newline, and ``|`` outside quotes)
and the domain appears in that same segment. A commit message, a grep
pattern, or a comment naming both the tool and the domain therefore
passes, and so does a fetch of some other host piped into a command
that mentions this one.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import re
import sys

_SEPARATOR_RE = re.compile(r"&&|\|\||;|\n|\|")
_DOMAIN_RE = re.compile(r"raw\.githubusercontent\.com")
_FETCH_HEAD_RE = re.compile(r"(curl|wget)(\s|$)")
_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*\s+")
_COMMAND_PREFIX_RE = re.compile(r"^(sudo|env|command|nohup|time)\s+")

REASON = (
    'Use gh instead: gh api repos/<owner>/<repo>/contents/<path> '
    '-H "Accept: application/vnd.github.raw". Fall back to the raw URL '
    "only if gh itself is unavailable — state that explicitly and ask "
    "the user."
)


def _split_outside_quotes(command: str) -> list[str]:
    """Split command by shell separators, ignoring separators inside quotes.

    >>> _split_outside_quotes("curl a | grep b")
    ['curl a ', ' grep b']
    >>> _split_outside_quotes("echo 'curl a | grep b'")
    ["echo 'curl a | grep b'"]
    >>> _split_outside_quotes("a && b || c ; d")
    ['a ', ' b ', ' c ', ' d']
    >>> _split_outside_quotes("a\\ncurl x")
    ['a', 'curl x']
    >>> _split_outside_quotes('echo "pipe | inside double"')
    ['echo "pipe | inside double"']
    """
    segments = []
    current = []
    in_single = False
    in_double = False
    i = 0
    while i < len(command):
        ch = command[i]

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


def _strip_leading_prefixes(segment: str) -> str:
    """Drop env assignments and wrappers that precede the real command.

    >>> _strip_leading_prefixes("HTTPS_PROXY=http://p curl x")
    'curl x'
    >>> _strip_leading_prefixes("sudo curl x")
    'curl x'
    >>> _strip_leading_prefixes("A=1 B=2 env curl x")
    'curl x'
    >>> _strip_leading_prefixes("curl x")
    'curl x'
    """
    previous = None
    while previous != segment:
        previous = segment
        segment = _ENV_ASSIGN_RE.sub("", segment)
        segment = _COMMAND_PREFIX_RE.sub("", segment)
    return segment


def is_raw_github_fetch(command: str) -> bool:
    """Return True if a segment invokes curl/wget against the domain.

    >>> is_raw_github_fetch("curl -sL https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("wget https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("cat urls | curl -K - https://raw.githubusercontent.com/a")
    True
    >>> is_raw_github_fetch("HTTPS_PROXY=http://p curl https://raw.githubusercontent.com/a")
    True

    Naming the tool and the domain without invoking one is not a fetch:

    >>> is_raw_github_fetch("git commit -m 'switch from curl to gh for raw.githubusercontent.com'")
    False
    >>> is_raw_github_fetch("git grep -n 'curl .*raw.githubusercontent.com'")
    False
    >>> is_raw_github_fetch("curl -sL https://example.com | grep raw.githubusercontent.com")
    False
    >>> is_raw_github_fetch("curl -sL https://example.com/a/b")
    False
    >>> is_raw_github_fetch("")
    False
    """
    for segment in _split_outside_quotes(command):
        segment = _strip_leading_prefixes(segment.strip())
        if _FETCH_HEAD_RE.match(segment) and _DOMAIN_RE.search(segment):
            return True
    return False


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_raw_github_fetch: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    command = data.get("tool_input", {}).get("command", "")

    if tool_name == "Bash" and is_raw_github_fetch(command):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON,
            },
        }))

    sys.exit(0)
