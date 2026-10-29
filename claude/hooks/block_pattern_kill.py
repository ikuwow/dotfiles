#!/usr/bin/env python3
"""Deny running ``pkill`` or ``killall`` by path, or a script containing them.

A pattern-based kill signals every process of the user whose name or
command line matches, so a short pattern reaches unrelated apps. The
deny rules in settings.json stop ``pkill`` and ``killall`` typed by
name, compound commands included, but a permission rule neither matches
the program invoked by path (``/usr/bin/pkill``) nor reads a script file
the command runs. This PreToolUse hook denies a simple command whose
program is named ``pkill`` or ``killall`` at any path, and a call that
runs a script file containing either word.

The program of a simple command is found after leading ``VAR=value``
assignments, the reserved words that open a compound command (``if``,
``then``, ``do``, ``{``, and the like), and the wrappers ``timeout``,
``time``, ``nice``, ``nohup``, ``stdbuf``, ``env``, ``command`` (other
than its ``-v`` / ``-V`` query form), ``builtin``, ``exec``, ``sudo``,
and ``xargs``, with their options. Heredoc bodies are data and are
skipped. A script is found where the command runs
it: as the first operand of a shell or another interpreter (``bash
x.sh``, ``python3 x.py``), of ``source`` or ``.``, or as a program path
containing ``/`` (``./x.sh``). A ``cd`` earlier in the same command
moves the directory a relative path resolves against, without regard to
subshells.

The hook leaves these open:

- A kill built from a PID lookup, such as ``pgrep -f x | xargs kill``
- A script that the found script itself runs, and a path held in a
  variable (``bash "$DIR/x.sh"``)
- A file containing a NUL byte, taken for a binary so that
  ``/opt/homebrew/bin/gh`` is not matched on its string table, and the
  part of a script past its first MiB

The script predicate asks only for either word anywhere in the file, so
a script that names ``pkill`` in a comment or a message is denied too,
and so is one that kills a process by its exact name, such as
``scripts/configure.sh``. This file itself is exempt, so it can be run
on crafted input.
A command that ``shlex`` cannot split, such as one using ``$'...'``
quoting, is denied when ``pkill`` or ``killall`` appears in it as a
word, and its scripts are not read.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import os
import re
import shlex
import sys

_PATTERN_KILL_RE = re.compile(rb"\b(pkill|killall)\b")
_PATTERN_KILL_WORD_RE = re.compile(r"(?:^|[\s;&|()])(?:\S*/)?(pkill|killall)(?=[\s;&|()]|$)")
_PATTERN_KILLERS = {"pkill", "killall"}
_SEPARATORS = {"&&", "||", ";", ";;", "|", "|&", "&", "(", ")"}
_SHELL_RE = re.compile(r"(ba|z|da|k)?sh")
_INTERPRETER_RE = re.compile(r"python[0-9.]*|perl|ruby|node")
_SOURCERS = {"source", "."}
# Each wrapper runs the command after its options, and the options listed
# take a value in the next word.
_WRAPPERS = {
    "time": set(),
    "nohup": set(),
    "command": set(),
    "builtin": set(),
    "exec": {"-a"},
    "nice": {"-n", "--adjustment"},
    "env": {"-u", "-C", "-S", "-P", "--unset", "--chdir", "--split-string"},
    "stdbuf": {"-i", "-o", "-e", "--input", "--output", "--error"},
    "timeout": {"-k", "-s", "--kill-after", "--signal"},
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-U", "--user", "--group"},
    "xargs": {"-n", "-I", "-J", "-L", "-P", "-R", "-S", "-a", "-d", "-E", "-s"},
}
# `timeout` takes its duration as an operand before the command.
_LEADING_OPERANDS = {"timeout": 1}
# A shell's -o and -O take an option name; its -c takes the code to run.
_SHELL_VALUE_OPTIONS = {"-o", "-O", "+o", "+O"}
# After these, other interpreters take the next word as the code to run.
_INLINE_CODE_OPTIONS = {"-c", "-e", "-E", "-m"}
# Words that open or continue a compound command come before the program
# of the simple command that follows them.
_RESERVED = {"if", "then", "else", "elif", "do", "while", "until", "!", "{"}
_ASSIGNMENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
_HEREDOC_RE = re.compile(r"(?<!<)<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
_MAX_READ = 1024 * 1024

_WHY = (
    "pkill and killall signal every process whose name or command line "
    "matches the pattern, unrelated user apps included. Stop only "
    "processes you started, by PID (kill <pid>)"
)
DIRECT_REASON = "{word} is a pattern-based kill. " + _WHY + "."
SCRIPT_REASON = (
    "{path} contains pkill or killall. " + _WHY
    + ", and edit the script to do the same before running it."
)


def _strip_heredocs(command: str) -> str:
    """Drop the bodies of heredocs, which are data rather than commands.

    >>> _strip_heredocs("git commit -F - <<'EOF'\\npkill is bad\\nEOF\\nls")
    "git commit -F - <<'EOF'\\nls"
    >>> _strip_heredocs("cat <<-X\\n\\tkillall\\n\\tX")
    'cat <<-X'
    """
    lines, pending = [], []
    for line in command.split("\n"):
        if pending:
            strip_tabs, delimiter = pending[0]
            if (line.lstrip("\t") if strip_tabs else line) == delimiter:
                pending.pop(0)
            continue
        lines.append(line)
        pending = [(m.group(1) == "-", m.group(3)) for m in _HEREDOC_RE.finditer(line)]
    return "\n".join(lines)


def _segments(command: str) -> list[list[str]]:
    """Split a command into the word lists of its simple commands.

    Heredoc bodies are dropped first. ``#`` is read as an ordinary
    character, so a comment stays a run of words and a ``#`` inside a word
    (``owner/repo#1``) does not cut the rest of the command off.

    >>> _segments("cd d && bash x.sh | tee out; ./y")
    [['cd', 'd'], ['bash', 'x.sh'], ['tee', 'out'], ['./y']]
    >>> _segments("echo 'a && b'")
    [['echo', 'a && b']]
    >>> _segments("# note\\n/usr/bin/pkill x")
    [['#', 'note'], ['/usr/bin/pkill', 'x']]
    >>> _segments("pr-watch add o/r#1 && ./y")
    [['pr-watch', 'add', 'o/r#1'], ['./y']]
    """
    lexer = shlex.shlex(
        _strip_heredocs(command).replace("\n", ";"), posix=True, punctuation_chars=True
    )
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


def _strip_prefixes(words: list[str]) -> list[str]:
    """Drop leading assignments and wrappers that run their operand.

    >>> _strip_prefixes(["FOO=1", "timeout", "-k", "5", "30", "nohup", "bash", "x"])
    ['bash', 'x']
    >>> _strip_prefixes(["env", "A=b", "stdbuf", "-oL", "./x"])
    ['./x']
    >>> _strip_prefixes(["nice", "-n", "10", "sudo", "-u", "me", "pkill", "x"])
    ['pkill', 'x']
    >>> _strip_prefixes(["xargs", "-n", "1", "/usr/bin/pkill"])
    ['/usr/bin/pkill']
    >>> _strip_prefixes(["then", "/usr/bin/pkill", "x"])
    ['/usr/bin/pkill', 'x']
    >>> _strip_prefixes(["command", "-v", "pkill"])
    ['command', '-v', 'pkill']
    """
    i = 0
    while i < len(words):
        word = words[i]
        name = os.path.basename(word)
        if _ASSIGNMENT_RE.match(word) or word in _RESERVED:
            i += 1
        elif name == "command" and words[i + 1:i + 2] in (["-v"], ["-V"]):
            # The query form looks a command up rather than running it.
            break
        elif name in _WRAPPERS:
            i += 1
            while i < len(words) and words[i].startswith("-"):
                i += 2 if words[i] in _WRAPPERS[name] else 1
            i += _LEADING_OPERANDS.get(name, 0)
        else:
            break
    return words[i:]


def _script_operand(words: list[str]) -> str:
    """Return the script operand of a shell, interpreter, or source command, or "".

    >>> _script_operand(["bash", "-e", "-o", "pipefail", "k.sh"])
    'k.sh'
    >>> _script_operand(["bash", "-c", "pkill x"])
    ''
    >>> _script_operand(["python3", "-u", "a.py"])
    'a.py'
    >>> _script_operand(["perl", "-e", "print 1"])
    ''
    """
    head = os.path.basename(words[0])
    if _SHELL_RE.fullmatch(head):
        value_options, code_options = _SHELL_VALUE_OPTIONS, {"-c"}
    elif _INTERPRETER_RE.fullmatch(head):
        value_options, code_options = set(), _INLINE_CODE_OPTIONS
    elif head in _SOURCERS:
        value_options, code_options = set(), set()
    else:
        return ""
    i = 1
    while i < len(words):
        arg = words[i]
        if arg in code_options:
            return ""
        if arg in value_options:
            i += 2
        elif arg.startswith(("-", "+")):
            i += 1
        else:
            return arg
    return ""


def script_paths(command: str, cwd: str) -> list[str]:
    """Return the paths of the scripts and programs a command runs by path.

    >>> script_paths("bash run.sh arg", "/w")
    ['/w/run.sh']
    >>> script_paths("cd sub && ./run.sh", "/w")
    ['/w/sub/run.sh']
    >>> script_paths("timeout 30 python3 -u /t/a.py", "/w")
    ['/t/a.py']
    >>> script_paths("source ~/x.sh", "/w") == [os.path.expanduser("~/x.sh")]
    True
    >>> script_paths("cd && ./x.sh", "/w") == [os.path.expanduser("~/x.sh")]
    True

    Inline code and plain commands name no script file:

    >>> script_paths("python3 -c 'print(1)'", "/w")
    []
    >>> script_paths("git commit -m 'add a pkill guard'", "/w")
    []
    """
    paths = []
    for words in _segments(command):
        words = _strip_prefixes(words)
        if not words:
            continue
        if os.path.basename(words[0]) == "cd":
            if len(words) == 1:
                cwd = os.path.expanduser("~")
            elif words[1] != "-":
                cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        target = _script_operand(words)
        if not target and "/" in words[0]:
            target = words[0]
        if target:
            paths.append(os.path.normpath(os.path.join(cwd, os.path.expanduser(target))))
    return paths


def direct_pattern_kill(command: str) -> str:
    """Return the program word of a simple command that is pkill or killall, or "".

    >>> direct_pattern_kill("sleep 1 && /usr/bin/pkill -f x")
    '/usr/bin/pkill'
    >>> direct_pattern_kill("timeout 5 killall Finder")
    'killall'
    >>> direct_pattern_kill("echo a#b && /usr/bin/pkill -f x")
    '/usr/bin/pkill'
    >>> direct_pattern_kill("git commit -m 'deny pkill'")
    ''
    """
    for words in _segments(command):
        words = _strip_prefixes(words)
        if words and os.path.basename(words[0]) in _PATTERN_KILLERS:
            return words[0]
    return ""


def pattern_kill_script(command: str, cwd: str) -> str:
    """Return the first script the command runs that contains pkill or killall, or ""."""
    for path in script_paths(command, cwd):
        # This file names both words, and running it on crafted input is
        # how its behavior is checked.
        if os.path.realpath(path) == os.path.realpath(__file__):
            continue
        try:
            with open(path, "rb") as f:
                data = f.read(_MAX_READ)
        except OSError:
            continue
        if b"\x00" not in data and _PATTERN_KILL_RE.search(data):
            return path
    return ""


def deny_reason(command: str, cwd: str) -> str:
    """Return why the command is denied, or "" to let it run.

    A command shlex cannot split falls back to a word search:

    >>> deny_reason("/usr/bin/pkill -f foo; echo $'it\\\\'s'", "/w")[:41]
    '/usr/bin/pkill is a pattern-based kill. p'
    >>> deny_reason("echo $'it\\\\'s'", "/w")
    ''
    """
    try:
        word = direct_pattern_kill(command)
        if word:
            return DIRECT_REASON.format(word=word)
        path = pattern_kill_script(command, cwd)
        if path:
            return SCRIPT_REASON.format(path=path)
        return ""
    except ValueError:
        match = _PATTERN_KILL_WORD_RE.search(command)
        if match:
            return DIRECT_REASON.format(word=match.group(0).strip(" \t\n;&|()"))
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
