#!/usr/bin/env python3
"""Deny direct ``ssh`` / ``scp`` / ``sftp`` invocations from the Bash tool.

Remote shells and file transfers reach hosts outside this machine, so
Claude Code does not run them directly. Wrappers under other names are
unaffected: the hook matches the resolved command name exactly, and it
never sees the subprocesses a wrapper spawns.

The hook splits the command into shell segments (respecting quotes),
strips leading environment-variable assignments, an ``env`` wrapper,
shell reserved words and grouping (``do``, ``then``, ``!``, ``{``,
``(``, ...), and a fixed set of launcher prefixes (``exec``,
``command``, ``sudo``, ``nohup``, ``time``, ``nice``, ``timeout``,
``xargs``), and denies the segment when the resolved command, or the
last path component of it, is one of the blocked names. Command
substitutions (``$(...)`` and backticks outside single quotes) are
checked the same way. A segment whose quotes do not balance, such as
one where an apostrophe in a comment or heredoc body threw off quote
tracking, is re-checked line by line.

Key-management tools (``ssh-keygen``, ``ssh-add``, ...) and git's own
ssh transport stay allowed. Resolution is best-effort: a command nested
inside a quoted string (``bash -c 'ssh host'``) passes, and a heredoc
body line that starts with a blocked name is denied.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import shlex
import sys

from hook_utils import drop_env_prefix, split_outside_quotes

_BLOCKED = {"ssh", "scp", "sftp"}

_RESERVED = {"do", "then", "else", "elif", "if", "while", "until", "!", "{", "("}

_LAUNCHERS = {
    "exec", "command", "sudo", "nohup", "time", "nice", "timeout", "xargs",
}

# Launcher options whose value is a separate token. Options not listed
# here are treated as taking no value.
_LAUNCHER_VALUE_FLAGS = {
    "exec": {"-a"},
    "sudo": {
        "-u", "-g", "-h", "-p", "-r", "-t", "-C", "-D", "-R", "-T", "-U",
        "--user", "--group",
    },
    "nice": {"-n"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "xargs": {"-I", "-n", "-P", "-L", "-d", "-E", "-s", "-a"},
}

REASON = (
    "Direct ssh/scp/sftp is denied for Claude Code. "
    "If remote access is genuinely needed, ask the user to run it directly."
)


def _strip_prefixes(tokens: list[str]) -> list[str]:
    """Strip env, reserved-word, and launcher prefixes until the real command.

    ``command -v`` / ``command -V`` only look the name up, so they are
    returned untouched. For ``timeout``, the positional duration is
    skipped too.

    >>> _strip_prefixes(["sudo", "-u", "me", "timeout", "5", "ssh", "h"])
    ['ssh', 'h']
    >>> _strip_prefixes(["do", "ssh", "h"])
    ['ssh', 'h']
    >>> _strip_prefixes(["(ssh", "h)"])
    ['ssh', 'h)']
    >>> _strip_prefixes(["command", "-v", "ssh"])
    ['command', '-v', 'ssh']
    """
    while True:
        tokens = drop_env_prefix(tokens)
        if not tokens:
            return tokens
        if tokens[0] in _RESERVED:
            tokens = tokens[1:]
            continue
        if tokens[0].startswith("("):
            tokens = [tokens[0].lstrip("(")] + tokens[1:]
            continue
        if tokens[0] not in _LAUNCHERS:
            return tokens
        launcher = tokens[0]
        value_flags = _LAUNCHER_VALUE_FLAGS.get(launcher, set())
        i = 1
        while i < len(tokens) and tokens[i].startswith("-"):
            if launcher == "command" and tokens[i] in ("-v", "-V"):
                return tokens
            i += 2 if tokens[i] in value_flags else 1
        if launcher == "timeout":
            i += 1
        tokens = tokens[i:]


def _substitutions(command: str) -> list[str]:
    """Return the bodies of ``$(...)`` and backtick substitutions.

    Substitutions inside single quotes are not expanded by the shell and
    are skipped. Parentheses are matched by simple depth counting.

    >>> _substitutions("x=$(ssh host uptime); echo `scp a b:c`")
    ['ssh host uptime', 'scp a b:c']
    >>> _substitutions("echo '$(ssh host)'")
    []
    >>> _substitutions('echo "don\\'t $(ssh host)"')
    ['ssh host']
    """
    bodies: list[str] = []
    in_single = in_double = False
    i = 0
    while i < len(command):
        ch = command[i]
        if ch == "\\" and not in_single:
            i += 2
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif not in_single and command.startswith("$(", i):
            depth = 1
            j = i + 2
            while j < len(command) and depth:
                if command[j] == "(":
                    depth += 1
                elif command[j] == ")":
                    depth -= 1
                j += 1
            bodies.append(command[i + 2:j - 1] if depth == 0 else command[i + 2:])
            i = j
            continue
        elif not in_single and ch == "`":
            end = command.find("`", i + 1)
            if end < 0:
                end = len(command)
            bodies.append(command[i + 1:end])
            i = end + 1
            continue
        i += 1
    return bodies


def _segment_blocks(segment: str) -> bool:
    try:
        tokens = shlex.split(segment, comments=False, posix=True)
    except ValueError:
        if "\n" in segment:
            return any(blocks(line) for line in segment.split("\n"))
        return False
    tokens = _strip_prefixes(tokens)
    if not tokens:
        return False
    return tokens[0].rsplit("/", 1)[-1] in _BLOCKED


def blocks(command: str) -> bool:
    """Return True if any segment or substitution invokes ssh, scp, or sftp.

    Blocked (direct):
    >>> blocks("ssh host")
    True
    >>> blocks("ssh -p 2222 user@host uptime")
    True
    >>> blocks("scp file host:/tmp/")
    True
    >>> blocks("sftp host")
    True

    Blocked (absolute path, env prefix):
    >>> blocks("/usr/bin/ssh host")
    True
    >>> blocks("FOO=1 ssh host")
    True
    >>> blocks("env FOO=1 ssh host")
    True
    >>> blocks("env -i ssh host")
    True
    >>> blocks("env -u FOO ssh host")
    True

    Blocked (launcher prefixes):
    >>> blocks("exec ssh host")
    True
    >>> blocks("exec -a foo ssh host")
    True
    >>> blocks("command ssh host")
    True
    >>> blocks("sudo ssh host")
    True
    >>> blocks("sudo -u root ssh host")
    True
    >>> blocks("sudo --user root ssh host")
    True
    >>> blocks("nohup ssh host")
    True
    >>> blocks("time ssh host")
    True
    >>> blocks("nice -n 10 ssh host")
    True
    >>> blocks("timeout 10 ssh host")
    True
    >>> blocks("timeout -s KILL 10 ssh host")
    True
    >>> blocks("echo h | xargs -I{} ssh {} uptime")
    True

    Blocked (reserved words and grouping):
    >>> blocks("for h in a b; do ssh $h uptime; done")
    True
    >>> blocks("while read h; do scp f $h:/tmp; done < hosts")
    True
    >>> blocks("if true; then ssh host; fi")
    True
    >>> blocks("! ssh host")
    True
    >>> blocks("{ ssh host; }")
    True
    >>> blocks("(ssh host)")
    True

    Blocked (command substitution):
    >>> blocks("x=$(ssh host cat /etc/hosts)")
    True
    >>> blocks('echo "$(ssh host uptime)"')
    True
    >>> blocks("echo `ssh host uptime`")
    True

    Blocked (an apostrophe that bash does not treat as a quote):
    >>> blocks("# note: don't\\nssh host")
    True
    >>> blocks("cat <<'EOF' > /tmp/x\\ndon't\\nEOF\\nssh host")
    True
    >>> blocks("echo it\\\\'s fine; ssh host")
    True

    Blocked (piped, chained, backgrounded):
    >>> blocks("ssh host | tee out")
    True
    >>> blocks("true && ssh host")
    True
    >>> blocks("ssh host &")
    True

    Not blocked (key management and look-ups):
    >>> blocks("ssh-keygen -t ed25519")
    False
    >>> blocks("ssh-add -l")
    False
    >>> blocks("which ssh")
    False
    >>> blocks("command -v ssh")
    False
    >>> blocks("man ssh")
    False

    Not blocked (git transport, other command names):
    >>> blocks("git push")
    False
    >>> blocks("vssh default")
    False

    Not blocked (string only appears inside quotes):
    >>> blocks("git commit -m 'block ssh host'")
    False
    >>> blocks("echo \\"ssh host\\"")
    False
    >>> blocks("echo '$(ssh host)'")
    False
    """
    for segment in split_outside_quotes(command):
        if _segment_blocks(segment):
            return True
    return any(blocks(body) for body in _substitutions(command))


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
