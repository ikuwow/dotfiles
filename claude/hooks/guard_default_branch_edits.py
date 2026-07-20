#!/usr/bin/env python3
"""Deny once per session, then allow: guard default-branch edits.

git-essentials.md ("Never create or edit files on the default branch")
is a git-workflow precondition the model is expected to enforce on its
own, but retrospectives found edits landing on main before a branch
existed. Some repos (this dotfiles repo included) also have sessions
where the user genuinely wants direct default-branch work, so a
permission prompt on every Write/Edit is the wrong shape — it would
either interrupt the legitimate case repeatedly or train the user to
reflexively approve it.

This PreToolUse hook instead mirrors the UX of Claude Code's GitHub
Actions security pre-check: the first Write/Edit/NotebookEdit that
targets a non-ignored path on the default branch is denied outright,
with branch-first guidance and a sanctioned-retry clause. A marker
file then records that this session has already been warned for this
repo; every later attempt in the same session, same repo, is allowed
silently — covering the exceptional "yes, edit main directly" case
without a user prompt. The marker is keyed on ``session_id`` plus a
hash of the repo root and lives in ``tempfile.gettempdir()``, so it
does not persist or leak across sessions or repos.

Paths are resolved with ``os.path.realpath`` before any git check.
Files under this repository are routinely edited through their
``~/.claude/...`` symlinks (see this repo's CLAUDE.md, "Symlink
Architecture"); without resolving the symlink first, a git check
anchored at the symlink's own directory would miss that the write
actually lands inside this repository's working tree.

Every subprocess call is fail-open: a directory outside any git work
tree, a detached HEAD, an unset ``origin/HEAD``, or a ``git`` binary
that errors or times out all result in ``exit(0)`` rather than a false
deny. Expected fail-open cases (no work tree, detached HEAD, unset
``origin/HEAD``) exit silently; anything unexpected (a bug in this
hook, a git timeout) additionally prints a one-line stderr breadcrumb
so hook logs can distinguish "rule not violated" from "hook broken".
An unwritable temp directory does not suppress the deny — the marker
write is best-effort, and the deny still fires even if the session
cannot be remembered. The target path may not exist yet (Write
creates new files), so git commands are anchored at the nearest
existing ancestor directory instead of the path itself.

Spec: https://code.claude.com/docs/en/hooks
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

_ORIGIN_PREFIX = "refs/remotes/origin/"
_SESSION_ID_SANITIZE_RE = re.compile(r"[^A-Za-z0-9-]")


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


def sanitize_session_id(session_id: str) -> str:
    """Keep only ``[A-Za-z0-9-]`` characters from a session id.

    Used to build a safe marker filename from a value that arrives
    over stdin JSON and should not be trusted with path separators or
    other filesystem-meaningful characters.

    >>> sanitize_session_id("abc-123")
    'abc-123'
    >>> sanitize_session_id("abc/123 def")
    'abc123def'
    >>> sanitize_session_id("unknown")
    'unknown'
    >>> sanitize_session_id("")
    ''
    """
    return _SESSION_ID_SANITIZE_RE.sub("", session_id)


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


def _marker_path(session_id: str, repo_root: str) -> str:
    """Build the per-session, per-repo marker file path."""
    sid = sanitize_session_id(session_id) or "unknown"
    repokey = hashlib.sha1(repo_root.encode("utf-8")).hexdigest()[:12]
    return os.path.join(
        tempfile.gettempdir(), f"claude-guard-default-branch-{sid}-{repokey}"
    )


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(
            f"guard_default_branch_edits: stdin parse failed: {e}",
            file=sys.stderr,
        )
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path:
        sys.exit(0)

    session_id = data.get("session_id") or "unknown"

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

        marker = _marker_path(session_id, repo_root)
        if os.path.exists(marker):
            sys.exit(0)
    except Exception as e:
        print(f"guard_default_branch_edits: check failed: {e!r}", file=sys.stderr)
        sys.exit(0)

    try:
        with open(marker, "x", encoding="utf-8"):
            pass
    except OSError:
        pass

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"Write/Edit targets a non-ignored path on the default "
                f"branch '{current}' of {repo_root}. git-essentials "
                f"prohibits editing files on the default branch — branch "
                f"first (invoke the git-workflow skill). Only when the "
                f"user has explicitly asked for work directly on the "
                f"default branch, retry this edit: retries in this "
                f"session are allowed for this repo."
            ),
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
