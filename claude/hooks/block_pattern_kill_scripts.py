#!/usr/bin/env python3
"""Deny running a script file that contains ``pkill`` or ``killall``.

A pattern-based kill signals every process of the user whose name or
command line matches, so a short pattern reaches unrelated apps. The
deny rules in settings.json stop ``pkill`` and ``killall`` typed in the
command itself, compound commands included, but a permission rule does
not read a script file the command runs. This PreToolUse hook reads
that file and denies the call when it contains either word, so a stop
by PID is the remaining route.

A script is found where the command runs it: as the first operand of a
shell or another interpreter (``bash x.sh``, ``python3 x.py``), of
``source`` or ``.``, or as a command path containing ``/``
(``./x.sh``). Leading ``VAR=value`` assignments and the wrappers
``timeout``, ``time``, ``nice``, ``nohup``, ``stdbuf``, ``env``,
``command``, ``builtin``, and ``exec`` are skipped first. A ``cd``
earlier in the same command moves the directory a relative path
resolves against. Scripts that the found script itself runs are not
read.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import os
import re
import shlex
import sys

_PATTERN_KILL_RE = re.compile(r"\b(pkill|killall)\b")
_SEPARATORS = {"&&", "||", ";", ";;", "|", "|&", "&", "(", ")"}
_INTERPRETER_RE = re.compile(r"(ba|z|da|k)?sh|python[0-9.]*|perl|ruby|node")
_SOURCERS = {"source", "."}
_PLAIN_WRAPPERS = {"time", "nice", "nohup", "command", "builtin", "exec", "env"}
# Options after these take the next word as the code to run, so no script
# file follows.
_INLINE_CODE_OPTIONS = {"-c", "-e", "-E", "-m"}
_ASSIGNMENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
_MAX_READ = 1024 * 1024

REASON = (
    "{path} contains pkill or killall, which signal every process whose "
    "name or command line matches the pattern, unrelated user apps "
    "included. Stop only processes you started, by PID (kill <pid>), "
    "and edit the script to do the same before running it."
)


def _segments(command: str) -> list[list[str]]:
    """Split a command into the word lists of its simple commands.

    >>> _segments("cd d && bash x.sh | tee out; ./y")
    [['cd', 'd'], ['bash', 'x.sh'], ['tee', 'out'], ['./y']]
    >>> _segments("echo 'a && b'")
    [['echo', 'a && b']]
    """
    lexer = shlex.shlex(command.replace("\n", ";"), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    segments, current = [], []
    for token in lexer:
        if token in _SEPARATORS:
            segments.append(current)
            current = []
        else:
            current.append(token)
    segments.append(current)
    return [s for s in segments if s]


def _strip_prefixes(words: list[str]) -> list[str]:
    """Drop leading assignments and wrappers that run their operand.

    >>> _strip_prefixes(["FOO=1", "timeout", "-k", "5", "30", "nohup", "bash", "x"])
    ['bash', 'x']
    >>> _strip_prefixes(["env", "A=b", "stdbuf", "-oL", "./x"])
    ['./x']
    """
    i = 0
    while i < len(words):
        word = words[i]
        name = os.path.basename(word)
        if _ASSIGNMENT_RE.match(word):
            i += 1
        elif name in _PLAIN_WRAPPERS or name == "stdbuf":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 1
        elif name == "timeout":
            i += 1
            while i < len(words) and words[i].startswith("-"):
                # -k and -s take a value in the next word.
                i += 2 if words[i] in ("-k", "-s") else 1
            i += 1  # the duration
        else:
            break
    return words[i:]


def script_paths(command: str, cwd: str) -> list[str]:
    """Return the paths of the script files a command runs.

    >>> script_paths("bash run.sh arg", "/w")
    ['/w/run.sh']
    >>> script_paths("cd sub && ./run.sh", "/w")
    ['/w/sub/run.sh']
    >>> script_paths("timeout 30 python3 -u /t/a.py", "/w")
    ['/t/a.py']
    >>> script_paths("source ~/x.sh", "/w") == [os.path.expanduser("~/x.sh")]
    True

    Inline code and plain commands name no script file:

    >>> script_paths("python3 -c 'print(1)'", "/w")
    []
    >>> script_paths("git commit -m 'add a pkill guard'", "/w")
    []
    >>> script_paths("echo 'unbalanced", "/w")
    []
    """
    try:
        segments = _segments(command)
    except ValueError:
        return []
    paths = []
    for words in segments:
        words = _strip_prefixes(words)
        if not words:
            continue
        head = os.path.basename(words[0])
        target = None
        if head == "cd":
            if len(words) > 1:
                cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        if head in _SOURCERS or _INTERPRETER_RE.fullmatch(head):
            for arg in words[1:]:
                if arg in _INLINE_CODE_OPTIONS:
                    break
                if not arg.startswith("-"):
                    target = arg
                    break
        elif "/" in words[0]:
            target = words[0]
        if target:
            paths.append(os.path.normpath(os.path.join(cwd, os.path.expanduser(target))))
    return paths


def pattern_kill_script(command: str, cwd: str) -> str:
    """Return the first script the command runs that contains pkill or killall, or ""."""
    for path in script_paths(command, cwd):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read(_MAX_READ)
        except OSError:
            continue
        if _PATTERN_KILL_RE.search(text):
            return path
    return ""


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_pattern_kill_scripts: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)
    command = data.get("tool_input", {}).get("command", "")
    cwd = data.get("cwd") or os.getcwd()

    path = pattern_kill_script(command, cwd)
    if path:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON.format(path=path),
            },
        }))

    sys.exit(0)
