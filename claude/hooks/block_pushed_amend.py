#!/usr/bin/env python3
"""Deny ``git commit --amend`` when HEAD is already pushed.

Force push flags are denied in settings.json, so amending a pushed
commit leaves a branch that has diverged from its remote and cannot be
pushed. This PreToolUse hook denies that amend before it runs and
points at a fresh commit instead. An amend of a commit that no
remote-tracking ref contains stays local and passes.

The pushed check runs in the repository a ``git -C <dir>`` names,
resolved against the hook's ``cwd``, and otherwise in ``cwd`` itself.
It reads local remote-tracking refs, so a commit pushed from elsewhere
and not yet fetched counts as unpushed.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import os
import shlex
import subprocess
import sys

REASON = (
    "HEAD is already pushed to {refs}. Amending it would need a force "
    "push, which is blocked. Make a new commit with the change instead."
)

_SEPARATORS = {";", "&", "&&", "|", "||", "(", ")"}


def _command_tokens(command: str) -> list:
    """Return shell tokens up to the first heredoc or unbalanced quote.

    The lexer reads lazily, so a heredoc body is never tokenized and a
    quote it carries cannot hide the command line before it.

    >>> _command_tokens("git commit --amend -F - <<'EOF'\\nDon't\\nEOF")
    ['git', 'commit', '--amend', '-F', '-']
    >>> _command_tokens("git log | grep -- --amend;")
    ['git', 'log', '|', 'grep', '--', '--amend', ';']
    """
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    tokens = []
    try:
        for token in lexer:
            if token.startswith("<<"):
                break
            tokens.append(token)
    except ValueError:
        pass
    return tokens


def amend_target(command: str):
    """Return the ``-C`` directory of a ``git commit --amend``, if any.

    Returns ``"."`` for an amend without ``-C``, and None when the
    command carries no amend.

    >>> amend_target("git commit --amend")
    '.'
    >>> amend_target("git commit -a --amend -m 'fix'")
    '.'
    >>> amend_target("git -C repo commit --amend --no-edit")
    'repo'
    >>> amend_target("git -C a -C b commit --amend")
    'a/b'
    >>> amend_target("git add f && git commit --amend --no-edit")
    '.'
    >>> amend_target("git commit --amend -F - <<'EOF'\\nDon't block\\nEOF")
    '.'

    A flag inside a message or a heredoc body, or after another
    subcommand, is not an amend:

    >>> amend_target("git commit -m 'Allow --amend before push'")
    >>> amend_target("git commit -F - <<'EOF'\\nAllow --amend\\nEOF")
    >>> amend_target("git log | grep -- --amend")
    >>> amend_target("git log --amend")
    """
    segment = []
    for token in _command_tokens(command) + [";"]:
        if token not in _SEPARATORS:
            segment.append(token)
            continue
        if segment and segment[0] == "git":
            target = "."
            i = 1
            while i < len(segment) and segment[i].startswith("-"):
                if segment[i] in ("-C", "-c") and i + 1 < len(segment):
                    if segment[i] == "-C":
                        target = os.path.normpath(
                            os.path.join(target, segment[i + 1]))
                    i += 2
                else:
                    i += 1
            if (i < len(segment) and segment[i] == "commit"
                    and "--amend" in segment[i + 1:]):
                return target
        segment = []
    return None


def remote_refs_containing_head(repo: str) -> list:
    """Return the remote-tracking refs that contain HEAD in ``repo``.

    Symbolic refs such as ``origin/HEAD`` are left out. A git failure
    (not a repository, unborn HEAD) returns an empty list, which lets
    the amend through.
    """
    result = subprocess.run(
        ["git", "-C", repo, "for-each-ref", "--contains", "HEAD",
         "--format=%(if)%(symref)%(then)%(else)%(refname:short)%(end)",
         "refs/remotes"],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        return []
    return result.stdout.split()


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_pushed_amend: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    command = data.get("tool_input", {}).get("command", "")
    target = amend_target(command) if tool_name == "Bash" else None

    if target is not None:
        repo = os.path.join(data.get("cwd", "."), target)
        refs = remote_refs_containing_head(repo)
        if refs:
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": REASON.format(
                        refs=", ".join(refs)),
                },
            }))

    sys.exit(0)
