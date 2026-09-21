#!/usr/bin/env python3
"""Deny direct ``ssh`` / ``scp`` / ``sftp`` invocations from the Bash tool.

Remote shells and file transfers reach hosts outside this machine, so
Claude Code does not run them directly. A future wrapper script under a
different name is unaffected: the hook matches the resolved command
name exactly, and a subprocess the wrapper spawns is invisible to it.

The hook splits the command into shell segments (respecting quotes),
strips leading environment-variable assignments, an ``env`` wrapper,
and a fixed set of launcher prefixes (``exec``, ``command``, ``sudo``,
``nohup``, ``time``, ``nice``, ``timeout``), and denies the segment when
the resolved command is one of the blocked names or a path ending in
one. Key-management tools (``ssh-keygen``, ``ssh-add``, ...) and git's
own ssh transport stay allowed.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import shlex
import sys

from hook_utils import drop_env_prefix, split_outside_quotes

_BLOCKED = {"ssh", "scp", "sftp"}

_LAUNCHERS = {"exec", "command", "sudo", "nohup", "time", "nice", "timeout"}

# Launcher options whose value is a separate token.
_LAUNCHER_VALUE_FLAGS = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-R", "-T", "-U"},
    "nice": {"-n"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
}

REASON = (
    "Direct ssh/scp/sftp is denied for Claude Code. "
    "If remote access is genuinely needed, ask the user to run it directly."
)


def _strip_launchers(tokens: list[str]) -> list[str]:
    """Strip env prefixes and launcher prefixes until the real command.

    ``command -v`` / ``command -V`` only look the name up, so they are
    returned untouched.

    >>> _strip_launchers(["sudo", "-u", "me", "timeout", "5", "ssh", "h"])
    ['ssh', 'h']
    >>> _strip_launchers(["command", "-v", "ssh"])
    ['command', '-v', 'ssh']
    """
    while True:
        tokens = drop_env_prefix(tokens)
        if not tokens or tokens[0] not in _LAUNCHERS:
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


def _segment_blocks(segment: str) -> bool:
    try:
        tokens = shlex.split(segment, comments=False, posix=True)
    except ValueError:
        return False
    tokens = _strip_launchers(tokens)
    if not tokens:
        return False
    return tokens[0].rsplit("/", 1)[-1] in _BLOCKED


def blocks(command: str) -> bool:
    """Return True if any segment invokes ssh, scp, or sftp.

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

    Blocked (launcher prefixes):
    >>> blocks("exec ssh host")
    True
    >>> blocks("command ssh host")
    True
    >>> blocks("sudo ssh host")
    True
    >>> blocks("sudo -u root ssh host")
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
    """
    for segment in split_outside_quotes(command):
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
