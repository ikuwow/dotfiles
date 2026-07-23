#!/usr/bin/env python3
"""Show the PR/issue edit diff to the user before it happens.

Fires on ``PreToolUse`` events for ``Bash`` calls. When the command begins
with ``gh pr edit`` or ``gh issue edit`` (first three tokens) and carries a
title/body-overwriting flag (``--title``/``-t``, ``--body``/``-b``,
``--body-file``/``-F``, including the ``=``-joined long-option forms), this
fetches the current server-side title/body via ``gh {pr,issue} view``,
computes a diff against the new value (unified diff for the body,
one-line before/after for the title), and returns it via the hook
``systemMessage`` field so Claude Code renders it directly to the user —
without waiting on the agent to generate reply text.

This complements the existing ``PostToolUse`` reminder
(``remind_show_edit_diff.py``), which nudges the agent to paste a diff into
its own reply after the edit already ran. That reminder still depends on an
LLM turn and can be skipped; this hook computes and displays the diff itself,
before the edit executes, and is a fallback-safe no-op on any failure (parse
failure, gh error, unreadable ``--body-file``, PR not found, timeout, etc.)
so it never blocks the underlying command.

Registered under ``PreToolUse`` with ``matcher: "Bash"``. Set
``ENABLE_SHOW_PR_EDIT_DIFF=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#pretooluse
"""
import difflib
import json
import os
import shlex
import subprocess
import sys

_TITLE_FLAGS = frozenset({"--title", "-t"})
_BODY_FLAGS = frozenset({"--body", "-b"})
_BODY_FILE_FLAGS = frozenset({"--body-file", "-F"})
_SHELL_OPERATORS = frozenset({"&&", "||", "|", ";", "&", "\n"})

_MAX_DIFF_LINES = 400


def _parse_edit_command(command):
    """Parse a ``gh (pr|issue) edit`` command for title/body edit flags.

    Returns ``None`` when the command does not start with ``gh (pr|issue)
    edit`` (first three tokens) or shlex parsing fails, or when it matches
    but carries none of ``--title``/``-t``, ``--body``/``-b``,
    ``--body-file``/``-F``. Shell operators (``&&``, ``||``, ``|``, ``;``,
    ``&``, newline) terminate flag scanning, so a matching flag appearing
    after one belongs to a different command and is not returned.

    Otherwise returns a dict with ``kind`` (``"pr"``/``"issue"``), ``number``
    (str, or ``None`` when the positional id is omitted), and any of
    ``title``, ``body``, ``body_file`` present in the command.

    >>> _parse_edit_command("gh pr edit 123 --title 'new title'")
    {'kind': 'pr', 'number': '123', 'title': 'new title'}
    >>> _parse_edit_command("gh issue edit --body-file /tmp/x")
    {'kind': 'issue', 'number': None, 'body_file': '/tmp/x'}
    >>> _parse_edit_command("gh pr edit 5 --title=Foo --body=Bar")
    {'kind': 'pr', 'number': '5', 'title': 'Foo', 'body': 'Bar'}
    >>> _parse_edit_command("gh pr edit 1 --add-label foo") is None
    True
    >>> _parse_edit_command("gh pr create --title 'x'") is None
    True
    >>> _parse_edit_command("gh pr edit 1 -t 'new'")
    {'kind': 'pr', 'number': '1', 'title': 'new'}
    >>> _parse_edit_command("gh pr edit 123 --add-label foo && grep -F pat log") is None
    True
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    if len(tokens) < 3:
        return None
    if tokens[0] != "gh" or tokens[1] not in ("pr", "issue") or tokens[2] != "edit":
        return None

    kind = tokens[1]
    idx = 3
    number = None
    if (
        idx < len(tokens)
        and tokens[idx] not in _SHELL_OPERATORS
        and not tokens[idx].startswith("-")
    ):
        number = tokens[idx]
        idx += 1

    result = {"kind": kind, "number": number}
    i = idx
    while i < len(tokens):
        tok = tokens[i]
        if tok in _SHELL_OPERATORS:
            break
        flag, sep, inline_value = tok.partition("=")
        if flag in _TITLE_FLAGS or flag in _BODY_FLAGS or flag in _BODY_FILE_FLAGS:
            if sep:
                value = inline_value
            elif i + 1 < len(tokens) and tokens[i + 1] not in _SHELL_OPERATORS:
                value = tokens[i + 1]
                i += 1
            else:
                value = None
            if value is not None:
                if flag in _TITLE_FLAGS:
                    result["title"] = value
                elif flag in _BODY_FLAGS:
                    result["body"] = value
                else:
                    result["body_file"] = value
        i += 1

    if not any(key in result for key in ("title", "body", "body_file")):
        return None
    return result


def main():
    if os.environ.get("ENABLE_SHOW_PR_EDIT_DIFF", "1") == "0":
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    if not isinstance(data, dict):
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        sys.exit(0)
    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    parsed = _parse_edit_command(command)
    if parsed is None:
        sys.exit(0)

    has_title = "title" in parsed
    has_body = "body" in parsed or "body_file" in parsed
    if not has_title and not has_body:
        sys.exit(0)

    kind = parsed["kind"]
    number = parsed["number"]
    ref = f"{kind} #{number}" if number else f"{kind} (current branch)"

    try:
        new_body = None
        if has_body:
            if "body_file" in parsed:
                with open(parsed["body_file"], "r", encoding="utf-8") as f:
                    new_body = f.read()
            else:
                new_body = parsed["body"]

        fields = []
        if has_title:
            fields.append("title")
        if has_body:
            fields.append("body")

        view_cmd = ["gh", kind, "view"]
        if number:
            view_cmd.append(number)
        view_cmd.extend(["--json", ",".join(fields)])

        proc = subprocess.run(
            view_cmd, capture_output=True, text=True, timeout=15, check=False,
        )
        if proc.returncode != 0:
            sys.exit(0)
        view_data = json.loads(proc.stdout)
        if not isinstance(view_data, dict):
            sys.exit(0)

        lines = [f"== gh {kind} edit diff ({ref}) =="]

        if has_title:
            old_title = view_data.get("title", "")
            new_title = parsed["title"]
            if old_title == new_title:
                lines.append(f"[title unchanged: {old_title}]")
            else:
                lines.append(f"title: '{old_title}' -> '{new_title}'")

        if has_body:
            old_body = view_data.get("body") or ""
            diff_lines = list(difflib.unified_diff(
                old_body.splitlines(keepends=True),
                new_body.splitlines(keepends=True),
                fromfile="body (current)",
                tofile="body (new)",
                n=3,
            ))
            if len(diff_lines) > _MAX_DIFF_LINES:
                overflow = len(diff_lines) - _MAX_DIFF_LINES
                diff_lines = diff_lines[:_MAX_DIFF_LINES]
                diff_lines.append(f"... [truncated, {overflow} more lines]\n")
            if diff_lines:
                lines.extend(line.rstrip("\n") for line in diff_lines)
            else:
                lines.append("[body unchanged]")

        message = "\n".join(lines)
    except (
        OSError,
        UnicodeDecodeError,
        subprocess.TimeoutExpired,
        json.JSONDecodeError,
    ):
        sys.exit(0)

    print(json.dumps({"systemMessage": message}))
    sys.exit(0)


if __name__ == "__main__":
    main()
