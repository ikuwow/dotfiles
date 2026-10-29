#!/usr/bin/env python3
"""Deny running a script file that contains ``pkill`` or ``killall``.

A pattern-based kill signals every process of the user whose name or
command line matches, so a short pattern reaches unrelated apps. The
deny rules in settings.json stop ``pkill`` and ``killall`` written in
the command, but a permission rule does not read a script file the
command runs. This PreToolUse hook reads the script each simple command
runs and denies the call when the file contains either word.

The script of a simple command is the first operand of ``sh``, ``bash``,
or ``zsh`` when the command starts with the shell, with a wrapper such
as ``timeout`` (``timeout 30 bash x.sh``), or with a keyword such as
``then``, of ``source`` or ``.`` as the
first word, or the first word itself when it contains ``/`` (``./x.sh``). A relative path resolves
against the session's working directory.

The hook leaves these open:

- A script run by path behind a wrapper (``timeout 30 ./x.sh``), through
  another interpreter (``python3 x.py``), after a ``cd`` in the same
  command, or through a variable (``bash "$DIR/x.sh"``)
- A shell option that takes a value before the script
  (``bash -o pipefail x.sh``)
- A script that the found script itself runs
- A kill built from a PID lookup, such as ``pgrep -f x | xargs kill``
- ``pkill`` invoked by path (``/usr/bin/pkill``), which the deny rules
  do not match either
- A command that ``shlex`` cannot split, a file containing a NUL byte,
  and the part of a script past its first MiB

The file check asks only for either word anywhere in the file, so a
script that names ``pkill`` in a comment is denied too, and so is one
that kills a process by its exact name, such as ``scripts/configure.sh``.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import os
import re
import shlex
import sys

_PATTERN_KILL_RE = re.compile(rb"\b(pkill|killall)\b")
_SEPARATORS = {"&&", "||", ";", ";;", "|", "|&", "&", "(", ")"}
_SHELLS = {"sh", "bash", "zsh"}
_SOURCERS = {"source", "."}
_WRAPPERS = {"timeout", "time", "nice", "nohup", "stdbuf", "env", "command", "exec", "sudo",
             "then", "do", "else", "!"}
_ASSIGNMENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
_MAX_READ = 1024 * 1024

REASON = (
    "{path} contains pkill or killall, which signal every process whose "
    "name or command line matches the pattern, unrelated user apps "
    "included. Stop only processes you started, by PID (kill <pid>), and "
    "edit the script to do the same before running it."
)


def _segments(command: str) -> list[list[str]]:
    """Split a command into the word lists of its simple commands.

    ``#`` is read as an ordinary character, so a ``#`` inside a word
    (``owner/repo#1``) does not cut the rest of the command off.

    >>> _segments("cd d && bash x.sh | tee out; ./y")
    [['cd', 'd'], ['bash', 'x.sh'], ['tee', 'out'], ['./y']]
    >>> _segments("echo 'a && b'\\npr-watch add o/r#1")
    [['echo', 'a && b'], ['pr-watch', 'add', 'o/r#1']]
    """
    lexer = shlex.shlex(command.replace("\n", ";"), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    segments, current = [], []
    for token in lexer:
        if token in _SEPARATORS:
            segments.append(current)
            current = []
        else:
            current.append(token)
    segments.append(current)
    return [s for s in segments if s]


def _script(words: list[str]) -> str:
    """Return the script file a simple command runs, or "".

    >>> _script(["timeout", "30", "bash", "-e", "run.sh", "arg"])
    'run.sh'
    >>> _script(["DIR=/tmp", "./run.sh"])
    './run.sh'
    >>> _script(["source", "~/x.sh"])
    '~/x.sh'
    >>> _script(["bash", "-c", "pkill x"])
    ''
    >>> _script(["git", "commit", "-m", "bash x.sh"])
    ''
    >>> _script(["grep", "-n", "bash", "settings.json"])
    ''
    >>> _script(["then", "bash", "run.sh"])
    'run.sh'
    """
    while words and _ASSIGNMENT_RE.match(words[0]):
        words = words[1:]
    if not words:
        return ""
    wrapped = words[0] in _WRAPPERS
    for i, word in enumerate(words):
        if (os.path.basename(word) in _SHELLS and (i == 0 or wrapped)) \
                or (i == 0 and word in _SOURCERS):
            for arg in words[i + 1:]:
                if arg == "-c":
                    return ""
                if not arg.startswith(("-", "+")):
                    return arg
            return ""
    return words[0] if "/" in words[0] else ""


def deny_reason(command: str, cwd: str) -> str:
    """Return why the command is denied, or "" to let it run.

    >>> deny_reason("echo $'it\\\\'s'", "/w")
    ''
    """
    try:
        segments = _segments(command)
    except ValueError:
        return ""
    for words in segments:
        script = _script(words)
        if not script:
            continue
        path = os.path.join(cwd, os.path.expanduser(script))
        try:
            with open(path, "rb") as f:
                data = f.read(_MAX_READ)
        except OSError:
            continue
        if b"\x00" not in data and _PATTERN_KILL_RE.search(data):
            return REASON.format(path=path)
    return ""


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_pattern_kill: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)
    command = data.get("tool_input", {}).get("command", "")
    cwd = data.get("cwd") or os.getcwd()

    reason = deny_reason(command, cwd)
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            },
        }))

    sys.exit(0)
