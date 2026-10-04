#!/usr/bin/env python3
"""List the sub-issues of a viewed issue, with comment counts, in context.

Fires on ``PostToolUse`` events for ``Bash`` calls starting with
``gh issue view <N>``. The ``gh issue view`` output shows no comments of
sub-issues, so this injects each sub-issue's number, title, state, and
comment count through ``hookSpecificOutput.additionalContext`` as one JSON
array, letting Claude judge which sub-issues it still has to read. Any gh
failure, including a gh without the ``subIssues`` field, exits 0 silently.

Spec: https://code.claude.com/docs/en/hooks#posttooluse
"""
import json
import shlex
import subprocess
import sys


def _parse_view_args(command):
    """Return the ``gh`` args selecting the viewed issue, or ``None``.

    >>> _parse_view_args("gh issue view 461 --comments")
    ['461']
    >>> _parse_view_args("gh issue view -R foo/bar 12")
    ['12', '--repo', 'foo/bar']
    >>> _parse_view_args("gh pr view 461") is None
    True
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if tokens[:3] != ["gh", "issue", "view"]:
        return None
    rest = tokens[3:]
    refs = [t for i, t in enumerate(rest)
            if not t.startswith("-") and (i == 0 or rest[i - 1] not in ("-R", "--repo"))]
    if not refs:
        return None
    args = [refs[0]]
    for i, tok in enumerate(rest[:-1]):
        if tok in ("-R", "--repo"):
            args += ["--repo", rest[i + 1]]
    return args


def _gh_json(args):
    try:
        proc = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=15)
        return json.loads(proc.stdout) if proc.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def main():
    data = json.load(sys.stdin)
    if data.get("tool_response", {}).get("exit_code", 0) != 0:
        return
    args = _parse_view_args(data.get("tool_input", {}).get("command", ""))
    view = args and _gh_json(["issue", "view", *args, "--json", "subIssues"])
    nodes = (view or {}).get("subIssues", {}).get("nodes") or []
    if not nodes:
        return
    subs = []
    for node in nodes:
        comments = (_gh_json(["issue", "view", node["url"], "--json", "comments"]) or {}).get("comments")
        subs.append({
            "number": node["number"],
            "title": node["title"],
            "state": node["state"],
            "comments": len(comments) if comments is not None else None,
        })
    context = f"Sub-issues of {args[0]}: {json.dumps(subs, ensure_ascii=False)}"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": context}}))


if __name__ == "__main__":
    main()
