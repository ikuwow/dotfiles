#!/usr/bin/env python3
"""Inject the sub-issues of a viewed issue, with comment counts, into context.

Fires on ``PostToolUse`` events for ``Bash`` calls. When the command begins
with ``gh issue view <N>`` and the call succeeded, this fetches the issue's
sub-issues via ``gh issue view <N> --json subIssues`` and, for each one, its
comment count via ``gh issue view <url> --json comments``. The list of
number, title, state, and comment count is returned through
``hookSpecificOutput.additionalContext`` so Claude sees that comments exist
on sub-issues, which the ``gh issue view`` output itself does not show.
Comment bodies are not injected.

Fallback-safe on any failure (parse failure, gh error, a gh version without
the ``subIssues`` field, timeout, etc.): the hook exits 0 without output.

Registered under ``PostToolUse`` with ``matcher: "Bash"``. Set
``ENABLE_SHOW_SUB_ISSUES=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#posttooluse
"""
import json
import os
import shlex
import subprocess
import sys

_SHELL_OPERATORS = frozenset({"&&", "||", "|", ";", "&", "\n"})
_VALUE_FLAGS = frozenset({"--repo", "-R", "--json", "--jq", "-q", "--template", "-t"})
_WEB_FLAGS = frozenset({"--web", "-w"})

_GH_TIMEOUT = 15


def _parse_view_command(command):
    """Parse a ``gh issue view`` command into its issue ref and repo.

    Returns ``None`` when the command does not start with ``gh issue view``
    (first three tokens), shlex parsing fails, no issue ref is given, or
    ``--web``/``-w`` is set. Shell operators terminate argument scanning.

    Otherwise returns a dict with ``ref`` (number, ``#``-number, or URL as
    written) and ``repo`` (``--repo``/``-R`` value, or ``None``).

    >>> _parse_view_command("gh issue view 461")
    {'ref': '461', 'repo': None}
    >>> _parse_view_command("gh issue view 12 --repo foo/bar --comments")
    {'ref': '12', 'repo': 'foo/bar'}
    >>> _parse_view_command("gh issue view -R foo/bar --json title 12")
    {'ref': '12', 'repo': 'foo/bar'}
    >>> _parse_view_command("gh issue view --repo=foo/bar 12")
    {'ref': '12', 'repo': 'foo/bar'}
    >>> _parse_view_command("gh issue view https://github.com/foo/bar/issues/3")
    {'ref': 'https://github.com/foo/bar/issues/3', 'repo': None}
    >>> _parse_view_command("gh issue view 461 --web") is None
    True
    >>> _parse_view_command("gh pr view 461") is None
    True
    >>> _parse_view_command("gh issue view | head") is None
    True
    >>> _parse_view_command("gh issue list && gh issue view 1") is None
    True
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if tokens[:3] != ["gh", "issue", "view"]:
        return None

    ref = None
    repo = None
    i = 3
    while i < len(tokens):
        tok = tokens[i]
        if tok in _SHELL_OPERATORS:
            break
        flag, sep, inline_value = tok.partition("=")
        if flag in _WEB_FLAGS:
            return None
        if flag in _VALUE_FLAGS:
            if sep:
                value = inline_value
            elif i + 1 < len(tokens) and tokens[i + 1] not in _SHELL_OPERATORS:
                value = tokens[i + 1]
                i += 1
            else:
                value = None
            if flag in ("--repo", "-R"):
                repo = value
        elif not tok.startswith("-") and ref is None:
            ref = tok
        i += 1

    if ref is None:
        return None
    return {"ref": ref, "repo": repo}


def _format_context(ref, sub_issues, total_count, comment_counts):
    """Render the additionalContext text.

    ``comment_counts`` holds an int per sub-issue, or ``None`` when the
    count could not be fetched.

    >>> print(_format_context(
    ...     "461",
    ...     [{"number": 7, "title": "Child A", "state": "OPEN"},
    ...      {"number": 8, "title": "Child B", "state": "CLOSED"}],
    ...     3,
    ...     [2, None],
    ... ))
    Issue 461 has 3 sub-issue(s). Their comments are not in the gh issue view output; read each sub-issue that has comments before reporting on the issue's comments.
    - #7 [OPEN] Child A: 2 comment(s)
    - #8 [CLOSED] Child B: comment count unavailable
    - 1 more sub-issue(s) not listed
    """
    lines = [
        f"Issue {ref} has {total_count} sub-issue(s). Their comments are not "
        "in the gh issue view output; read each sub-issue that has comments "
        "before reporting on the issue's comments."
    ]
    for sub, count in zip(sub_issues, comment_counts):
        if count is None:
            count_text = "comment count unavailable"
        else:
            count_text = f"{count} comment(s)"
        lines.append(f"- #{sub.get('number')} [{sub.get('state')}] {sub.get('title')}: {count_text}")
    if total_count > len(sub_issues):
        lines.append(f"- {total_count - len(sub_issues)} more sub-issue(s) not listed")
    return "\n".join(lines)


def _gh_json(args):
    """Run ``gh`` with ``args`` and return parsed JSON, or ``None`` on failure."""
    try:
        proc = subprocess.run(
            ["gh", *args], capture_output=True, text=True,
            timeout=_GH_TIMEOUT, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _comment_count(url):
    data = _gh_json(["issue", "view", url, "--json", "comments"])
    if not isinstance(data, dict) or not isinstance(data.get("comments"), list):
        return None
    return len(data["comments"])


def main():
    if os.environ.get("ENABLE_SHOW_SUB_ISSUES", "1") == "0":
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    if not isinstance(data, dict) or data.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        sys.exit(0)
    tool_response = data.get("tool_response")
    if isinstance(tool_response, dict) and tool_response.get("exit_code", 0) != 0:
        sys.exit(0)

    parsed = _parse_view_command(tool_input.get("command", ""))
    if parsed is None:
        sys.exit(0)

    view_args = ["issue", "view", parsed["ref"], "--json", "subIssues"]
    if parsed["repo"]:
        view_args.extend(["--repo", parsed["repo"]])
    view_data = _gh_json(view_args)
    if not isinstance(view_data, dict):
        sys.exit(0)
    sub_field = view_data.get("subIssues")
    if not isinstance(sub_field, dict):
        sys.exit(0)
    sub_issues = sub_field.get("nodes") or []
    if not sub_issues:
        sys.exit(0)
    total_count = sub_field.get("totalCount") or len(sub_issues)

    comment_counts = [_comment_count(sub.get("url", "")) for sub in sub_issues]
    context = _format_context(parsed["ref"], sub_issues, total_count, comment_counts)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
