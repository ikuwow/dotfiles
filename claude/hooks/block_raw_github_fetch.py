#!/usr/bin/env python3
"""Deny curl/wget fetches of raw.githubusercontent.com in favor of ``gh``.

Fetching raw.githubusercontent.com directly is only warranted when
``gh`` itself is unavailable. This PreToolUse hook carries that
constraint: a Bash command that reaches for ``curl``/``wget`` against
that domain is denied and pointed at the ``gh api`` equivalent instead,
with the "ask the user" fallback for the case where ``gh`` cannot run.
The predicate asks for the domain and the word ``curl`` or ``wget``
anywhere in the command, without relating their positions. A command
that only names the domain passes; one that names it alongside either
word is denied even when it fetches nothing, which covers a commit
message or a grep pattern carrying both.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import re
import sys

_DOMAIN_RE = re.compile(r"raw\.githubusercontent\.com")
_FETCH_TOOL_RE = re.compile(r"\b(curl|wget)\b")

REASON = (
    'Use gh instead: gh api repos/<owner>/<repo>/contents/<path> '
    '-H "Accept: application/vnd.github.raw". Fall back to the raw URL '
    "only if gh itself is unavailable — state that explicitly and ask "
    "the user."
)


def is_raw_github_fetch(command: str) -> bool:
    """Return True if raw.githubusercontent.com and curl/wget both appear.

    >>> is_raw_github_fetch("curl -sL https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("wget https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("git commit -m 'mentions raw.githubusercontent.com'")
    False

    Both words in one command are enough, whatever their positions:

    >>> is_raw_github_fetch("git grep -n 'curl .*raw.githubusercontent.com'")
    True
    >>> is_raw_github_fetch("curl -sL https://example.com/a/b")
    False
    >>> is_raw_github_fetch("")
    False
    """
    return bool(_DOMAIN_RE.search(command) and _FETCH_TOOL_RE.search(command))


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
