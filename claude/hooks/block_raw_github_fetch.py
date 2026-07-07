#!/usr/bin/env python3
"""Deny curl/wget fetches of raw.githubusercontent.com in favor of ``gh``.

AIRULES.md ("GitHubの操作は...`gh` コマンドを使う。ghが使えない環境や
ghで実現できない操作の場合のみ...`raw.githubusercontent.com` 等を使って
よい") only permits fetching raw.githubusercontent.com directly when
``gh`` itself is unavailable. This PreToolUse hook mechanizes the
default case: a Bash command that reaches for ``curl``/``wget`` against
that domain is denied and pointed at the ``gh api`` equivalent instead.
The predicate is narrowed to ``curl``/``wget`` invocations (not any
mention of the domain) so commands that merely reference the domain in
passing — a commit message, a comment, a grep pattern — are not
tripped.

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
    """Return True if command fetches raw.githubusercontent.com via curl/wget.

    >>> is_raw_github_fetch("curl -sL https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("wget https://raw.githubusercontent.com/a/b/main/x")
    True
    >>> is_raw_github_fetch("git commit -m 'mentions raw.githubusercontent.com'")
    False
    >>> is_raw_github_fetch("curl -sL https://example.com/a/b")
    False
    >>> is_raw_github_fetch("")
    False
    """
    return bool(_DOMAIN_RE.search(command) and _FETCH_TOOL_RE.search(command))


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
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
