#!/usr/bin/env python3
"""Ask before Write/Edit/NotebookEdit touches a tracked file on the default branch.

git-essentials.md ("Never create or edit files on the default branch")
is a git-workflow precondition the model is expected to enforce on its
own, but retrospectives found edits landing on main before a branch
existed. This PreToolUse hook raises that case as a permission prompt
rather than blocking it outright ("ask", not "deny"): the check fires
in every repo, including ones where a user-instructed default-branch
edit is genuinely intended (a quick fix directly on someone else's
throwaway repo, a repo with no branching workflow at all, etc.), and
denying outright would remove that legitimate path.

Paths are resolved with ``os.path.realpath`` before any git check.
Files under this repository are routinely edited through their
``~/.claude/...`` symlinks (see this repo's CLAUDE.md, "Symlink
Architecture"); without resolving the symlink first, a git check
anchored at the symlink's own directory would miss that the write
actually lands inside this repository's working tree.

Every subprocess call is fail-open: a directory outside any git work
tree, a detached HEAD, an unset ``origin/HEAD``, or a ``git`` binary
that errors or times out all result in a silent ``exit(0)`` rather
than a false "ask". The target path may not exist yet (Write creates
new files), so git commands are anchored at the nearest existing
ancestor directory instead of the path itself.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import os
import subprocess
import sys

_ORIGIN_PREFIX = "refs/remotes/origin/"


def strip_origin_prefix(ref: str) -> str:
    """Strip a leading ``refs/remotes/origin/`` from a ref name.

    >>> strip_origin_prefix("refs/remotes/origin/main")
    'main'
    >>> strip_origin_prefix("refs/remotes/origin/release/1.0")
    'release/1.0'
    >>> strip_origin_prefix("main")
    'main'
    >>> strip_origin_prefix("")
    ''
    """
    if ref.startswith(_ORIGIN_PREFIX):
        return ref[len(_ORIGIN_PREFIX):]
    return ref


def nearest_existing_dir(path: str) -> str:
    """Return the nearest existing ancestor directory of ``path``.

    Walks up from ``path`` until an existing directory is found. This
    needs the filesystem, so it is not doctested here.
    """
    current = path
    while current and not os.path.isdir(current):
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return current or os.sep


def _run_git(args, cwd):
    return subprocess.run(
        ["git", "-C", cwd] + args,
        capture_output=True,
        text=True,
        timeout=5,
    )


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path:
        sys.exit(0)

    try:
        real = os.path.realpath(path)
        start_dir = nearest_existing_dir(real)

        result = _run_git(["rev-parse", "--is-inside-work-tree"], start_dir)
        if result.returncode != 0 or result.stdout.strip() != "true":
            sys.exit(0)

        result = _run_git(["check-ignore", "-q", real], start_dir)
        if result.returncode == 0:
            sys.exit(0)

        result = _run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], start_dir)
        if result.returncode != 0:
            sys.exit(0)
        current = result.stdout.strip()

        result = _run_git(
            ["symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"], start_dir
        )
        if result.returncode != 0:
            sys.exit(0)
        default = strip_origin_prefix(result.stdout.strip())

        if current != default:
            sys.exit(0)

        result = _run_git(["rev-parse", "--show-toplevel"], start_dir)
        repo_root = result.stdout.strip() if result.returncode == 0 else start_dir
    except Exception:
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Write/Edit targets a tracked path on the default branch "
                f"'{current}' of {repo_root}. git-essentials prohibits "
                f"editing files on the default branch — branch first "
                f"(invoke the git-workflow skill). Approve only if editing "
                f"on the default branch is genuinely intended."
            ),
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
