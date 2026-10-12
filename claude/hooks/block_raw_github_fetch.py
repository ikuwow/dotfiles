#!/usr/bin/env python3
"""Deny curl/wget fetches of raw.githubusercontent.com in favor of ``gh``.

Fetching raw.githubusercontent.com directly is only warranted when
``gh`` itself is unavailable. This PreToolUse hook carries that
constraint: a Bash command that reaches for ``curl``/``wget`` against
that domain is denied and pointed at the ``gh api`` equivalent instead,
with the "ask the user" fallback for the case where ``gh`` cannot run.

The predicate asks for an invocation, not a mention. Line continuations
are joined, the command is split on ``&&``, ``||``, ``;``, newline, and
``|`` outside quotes, and each segment is denied when it names the
domain and puts a fetch tool in command position — at the head of the
segment, after a leading environment assignment or a wrapper such as
``sudo`` or ``timeout``, or opening a substitution or subshell. A path
qualifier such as ``/usr/bin/`` is accepted on the tool name.

So a commit message, a grep pattern, or a comment naming both the tool
and the domain passes, and so does a fetch of some other host piped
into a command that mentions this one. Two shapes still match without
fetching the domain: a heredoc body, whose lines are read as commands,
and a fetch of another host that carries the domain elsewhere on the
same segment, such as in a header value or an output filename.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import re
import sys

_CONTINUATION_RE = re.compile(r"\\\n")
_SEPARATOR_RE = re.compile(r"&&|\|\||;|\n|\|")
_DOMAIN_RE = re.compile(r"raw\.githubusercontent\.com")
_FETCH_COMMAND_RE = re.compile(r"(?:^|[(`]|\$\()\s*(?:\S*/)?(?:curl|wget)(\s|$)")
_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=[^\s$]*\s+")
_WRAPPER_RE = re.compile(r"^(?:sudo|env|command|nohup|time)\s+|^timeout\s+\S+\s+")

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
    """Drop env assignments and the wrappers named in ``_WRAPPER_RE``.

    Each pass removes a prefix of at least two characters, so the loop
    ends on every input.

    >>> _strip_leading_prefixes("HTTPS_PROXY=http://p curl x")
    'curl x'
    >>> _strip_leading_prefixes("sudo curl x")
    'curl x'
    >>> _strip_leading_prefixes("timeout 10 curl x")
    'curl x'
    >>> _strip_leading_prefixes("A=1 B=2 env curl x")
    'curl x'
    >>> _strip_leading_prefixes("curl x")
    'curl x'

    An assignment whose value opens a substitution is left alone, so the
    tool inside it stays visible:

    >>> _strip_leading_prefixes("content=$(curl x)")
    'content=$(curl x)'
    """
    previous = None
    while previous != segment:
        previous = segment
        segment = _ENV_ASSIGN_RE.sub("", segment)
        segment = _WRAPPER_RE.sub("", segment)
    return segment


def is_raw_github_fetch(command: str) -> bool:
    """Return True if a segment names the domain and invokes curl/wget.

    >>> is_raw_github_fetch("curl -sL https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("wget https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("cat urls | curl -K - https://raw.githubusercontent.com/a")
    True

    Command position survives an assignment, a wrapper, a path
    qualifier, a substitution, and a line continuation:

    >>> is_raw_github_fetch("HTTPS_PROXY=http://p curl https://raw.githubusercontent.com/a")
    True
    >>> is_raw_github_fetch("timeout 10 curl https://raw.githubusercontent.com/a")
    True
    >>> is_raw_github_fetch("/usr/bin/curl -sL https://raw.githubusercontent.com/a")
    True
    >>> is_raw_github_fetch('bash -c "$(curl -fsSL https://raw.githubusercontent.com/a)"')
    True
    >>> is_raw_github_fetch("body=$(curl -sL https://raw.githubusercontent.com/a)")
    True
    >>> is_raw_github_fetch("curl -sL \\\\\\n  https://raw.githubusercontent.com/a")
    True

    Naming the tool and the domain without putting the tool in command
    position is not a fetch:

    >>> is_raw_github_fetch("git commit -m 'switch from curl to gh for raw.githubusercontent.com'")
    False
    >>> is_raw_github_fetch("git grep -n 'curl .*raw.githubusercontent.com'")
    False

    Neither is a fetch whose domain sits in another segment, or none:

    >>> is_raw_github_fetch("curl -sL https://example.com | grep raw.githubusercontent.com")
    False
    >>> is_raw_github_fetch("curl -sL https://example.com/a/b")
    False
    >>> is_raw_github_fetch("")
    False
    """
    command = _CONTINUATION_RE.sub(" ", command)
    for segment in _split_outside_quotes(command):
        segment = _strip_leading_prefixes(segment.strip())
        if _DOMAIN_RE.search(segment) and _FETCH_COMMAND_RE.search(segment):
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
