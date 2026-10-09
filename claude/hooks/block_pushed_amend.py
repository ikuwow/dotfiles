#!/usr/bin/env python3
"""Deny ``git commit --amend`` when HEAD is already pushed.

Force push is denied in settings.json, so amending a pushed commit
leaves a branch that has diverged from its remote and cannot be pushed.
This PreToolUse hook denies that amend before it runs and points at a
fresh commit instead. An amend of a commit that no remote-tracking ref
contains stays local and passes.

The pushed check reads local remote-tracking refs, so a commit pushed
from elsewhere and not yet fetched counts as unpushed.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import shlex
import subprocess
import sys

REASON = (
    "HEAD is already pushed to {refs}. Amending it would need a force "
    "push, which is blocked. Make a new commit with the change instead."
)


def is_amend_commit(command: str) -> bool:
    """Return True if a ``git`` token is followed by ``commit`` and ``--amend``.

    >>> is_amend_commit("git commit --amend")
    True
    >>> is_amend_commit("git commit --amend --no-edit")
    True
    >>> is_amend_commit("git commit -a --amend -m 'fix'")
    True
    >>> is_amend_commit("git -C repo commit --amend")
    True

    A message that mentions the flag is a single token and passes:

    >>> is_amend_commit("git commit -m 'Allow --amend before push'")
    False
    >>> is_amend_commit("git commit -m 'fix'")
    False
    >>> is_amend_commit("git log --amend")
    False

    Unbalanced quotes cannot be tokenized and pass:

    >>> is_amend_commit("git commit --amend -m 'oops")
    False
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False
    if "git" not in tokens:
        return False
    rest = tokens[tokens.index("git") + 1:]
    if "commit" not in rest:
        return False
    return "--amend" in rest[rest.index("commit") + 1:]


def remote_refs_containing_head(cwd: str) -> list:
    """Return the remote-tracking refs that contain HEAD in ``cwd``."""
    result = subprocess.run(
        ["git", "-C", cwd, "for-each-ref", "--contains", "HEAD",
         "--format=%(refname:short)", "refs/remotes"],
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

    if tool_name == "Bash" and is_amend_commit(command):
        refs = remote_refs_containing_head(data.get("cwd", "."))
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
