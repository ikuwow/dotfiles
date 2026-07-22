#!/usr/bin/env python3
"""Deny ``aws logs start-query`` invocations regardless of profile or option shape.

CloudWatch Logs Insights ``start-query`` can scan large volumes of log
data. Block it at the permission layer so no allow rule (e.g. the
``AWS_PROFILE=*-ro aws *`` read-only bundles) can implicitly authorize
it, and so the block is not bypassed by option-position tricks that a
glob-based ``permissions.deny`` entry would miss.

The hook splits the command into shell segments (respecting quotes),
strips leading environment-variable assignments and an optional
``env ...`` wrapper from each segment, and denies the segment when the
resolved command is ``aws`` (or a path ending in ``/aws``) with
service ``logs`` and subcommand ``start-query``.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import re
import shlex
import sys

_SEPARATOR_RE = re.compile(r"&&|\|\||;|\||&|\n")
_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

_AWS_GLOBAL_VALUE_FLAGS = {
    "--profile",
    "--region",
    "--output",
    "--endpoint-url",
    "--ca-bundle",
    "--cli-connect-timeout",
    "--cli-read-timeout",
    "--query",
    "--color",
    "--cli-input-yaml",
    "--cli-input-json",
    "--cli-binary-format",
    "--cli-pager",
    "--cli-auto-prompt",
}

REASON = (
    "aws logs start-query is denied. CloudWatch Logs Insights queries "
    "can scan large volumes of log data and are billed by scanned "
    "bytes. If genuinely needed, ask the user to run it directly."
)


def _split_outside_quotes(command: str) -> list[str]:
    """Split by shell separators, ignoring separators inside quotes.

    >>> _split_outside_quotes("aws logs start-query | jq .")
    ['aws logs start-query ', ' jq .']
    >>> _split_outside_quotes("echo 'aws logs start-query | jq .'")
    ["echo 'aws logs start-query | jq .'"]
    >>> _split_outside_quotes("foo && aws logs start-query")
    ['foo ', ' aws logs start-query']
    """
    segments: list[str] = []
    current: list[str] = []
    in_single = in_double = False
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


def _drop_env_prefix(tokens: list[str]) -> list[str]:
    """Strip leading ``KEY=VALUE`` assignments and an optional ``env`` wrapper."""
    i = 0
    while i < len(tokens) and _ENV_ASSIGN_RE.match(tokens[i]):
        i += 1
    if i < len(tokens) and tokens[i] == "env":
        i += 1
        while i < len(tokens) and _ENV_ASSIGN_RE.match(tokens[i]):
            i += 1
    return tokens[i:]


def _is_aws(tok: str) -> bool:
    return tok == "aws" or tok.endswith("/aws")


def _next_positional(tokens: list[str], start: int) -> int:
    """Return index of next positional (non-option) token, treating known
    aws global flags with values in space form as consuming the next token."""
    i = start
    while i < len(tokens):
        t = tokens[i]
        if not t.startswith("-"):
            return i
        if "=" in t:
            i += 1
            continue
        if t in _AWS_GLOBAL_VALUE_FLAGS:
            i += 2
        else:
            i += 1
    return -1


def _segment_blocks(segment: str) -> bool:
    try:
        tokens = shlex.split(segment, comments=False, posix=True)
    except ValueError:
        return False
    tokens = _drop_env_prefix(tokens)
    if not tokens or not _is_aws(tokens[0]):
        return False
    i = _next_positional(tokens, 1)
    if i < 0 or tokens[i] != "logs":
        return False
    j = _next_positional(tokens, i + 1)
    return j > 0 and tokens[j] == "start-query"


def blocks(command: str) -> bool:
    """Return True if any segment invokes ``aws logs start-query``.

    Blocked (direct):
    >>> blocks("aws logs start-query --log-group-name /aws/lambda/foo --query-string 'fields @timestamp'")
    True
    >>> blocks("aws logs start-query")
    True

    Blocked (env-var prefix, single and multiple):
    >>> blocks("AWS_PROFILE=stg-ro aws logs start-query --log-group-name x")
    True
    >>> blocks("AWS_PROFILE=stg-ro AWS_REGION=us-east-1 aws logs start-query")
    True

    Blocked (``env`` wrapper):
    >>> blocks("env AWS_PROFILE=stg-ro aws logs start-query")
    True

    Blocked (global option before service):
    >>> blocks("aws --profile stg-ro logs start-query")
    True
    >>> blocks("aws --profile=stg-ro logs start-query")
    True
    >>> blocks("aws --profile stg-ro --region us-east-1 logs start-query")
    True

    Blocked (absolute path):
    >>> blocks("/opt/homebrew/bin/aws logs start-query")
    True

    Blocked (piped, chained, backgrounded):
    >>> blocks("aws logs start-query | jq .")
    True
    >>> blocks("foo && aws logs start-query")
    True
    >>> blocks("aws logs start-query &")
    True

    Not blocked (different subcommand):
    >>> blocks("aws logs describe-log-groups")
    False
    >>> blocks("aws logs filter-log-events --log-group-name /aws/lambda/foo")
    False
    >>> blocks("aws logs get-query-results --query-id abc")
    False

    Not blocked (string only appears inside quotes — commit message, PR body):
    >>> blocks("git commit -m 'block aws logs start-query'")
    False
    >>> blocks("gh pr create --title 'Deny aws logs start-query'")
    False
    >>> blocks("echo \\"aws logs start-query\\"")
    False

    Not blocked (option value happens to be ``logs`` / ``start-query``):
    >>> blocks("aws --profile logs s3 ls")
    False

    Not blocked (help lookup with ``help`` before subcommand):
    >>> blocks("aws logs help")
    False
    """
    for segment in _split_outside_quotes(command):
        if _segment_blocks(segment):
            return True
    return False


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    command = data.get("tool_input", {}).get("command", "")

    if tool_name == "Bash" and blocks(command):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON,
            },
        }))

    sys.exit(0)
