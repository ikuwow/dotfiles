#!/usr/bin/env python3
"""Deny gh issue/PR creation that would carry private-repository work into a public one.

Fires on ``PreToolUse`` events for ``Bash`` calls whose command begins
with ``gh issue create`` or ``gh pr create``:

- Without ``--repo``, the call is denied and asked to name the target
  explicitly, so the destination is always on the command line instead
  of being resolved by gh from the working directory
- With ``--repo``, the call is denied when the working directory's
  repository is not public and the target is public

Runs at ``PreToolUse`` because ``approve_git_gh_commands.py``
auto-approves both commands at ``PermissionRequest``. Visibility comes
from ``gh api repos/<owner>/<repo>``; any failure there fails open.

Spec: https://code.claude.com/docs/en/hooks#pretooluse
"""
import json
import shlex
import subprocess
import sys

MISSING_REPO = (
    "Name the target repository explicitly with --repo OWNER/REPO (long "
    "form) and re-run, so the destination is visible on the command line."
)
PRIVATE_TO_PUBLIC = (
    "Blocked: the working directory is the non-public repository {source}, "
    "and --repo targets the public repository {target}. Content from a "
    "private repository must not be published there. Tell the user what "
    "you were about to post and where."
)


def parse_create(command):
    """Return ``(True, repo)`` for a gh issue/PR create command, else ``(False, None)``.

    ``repo`` is the ``--repo`` value, or None when the flag is absent.

    >>> parse_create("gh issue create --repo ikuwow/dotfiles --title t")
    (True, 'ikuwow/dotfiles')
    >>> parse_create("gh pr create --draft --repo=o/r --body-file b")
    (True, 'o/r')
    >>> parse_create("gh pr create --draft --body-file b")
    (True, None)
    >>> parse_create("gh issue create -R o/r --title t")
    (True, None)
    >>> parse_create("gh pr view 3")
    (False, None)
    >>> parse_create("gh issue create --title 'unterminated")
    (False, None)

    The last ``--repo`` wins, matching gh, and any ``-R`` voids the
    value since gh could pick it over ``--repo``:

    >>> parse_create("gh issue create --repo a/private --repo b/public")
    (True, 'b/public')
    >>> parse_create("gh issue create --repo a/private -R b/public")
    (True, None)
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return False, None
    if tokens[:1] != ["gh"] or tokens[1:2] not in (["issue"], ["pr"]) or tokens[2:3] != ["create"]:
        return False, None
    args = tokens[3:]
    repo = None
    for i, tok in enumerate(args):
        if tok.startswith("-R"):
            return True, None
        if tok.startswith("--repo="):
            repo = tok[len("--repo="):]
        elif tok == "--repo" and i + 1 < len(args):
            repo = args[i + 1]
    return True, repo


def visibility(repo, cwd):
    """Return ``(full_name, visibility)``, or None when gh cannot tell."""
    path = f"repos/{repo}" if repo else "repos/{owner}/{repo}"
    try:
        proc = subprocess.run(
            ["gh", "api", path, "--jq", '[.full_name, .visibility] | join(" ")'],
            capture_output=True, text=True, timeout=15, check=False, cwd=cwd or None,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"guard_public_publish: gh api failed: {e}", file=sys.stderr)
        return None
    parts = proc.stdout.split()
    if proc.returncode != 0 or len(parts) != 2:
        print(f"guard_public_publish: gh api {path} gave no visibility", file=sys.stderr)
        return None
    return parts[0], parts[1]


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }))
    sys.exit(0)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    if not isinstance(data, dict) or data.get("tool_name") != "Bash":
        sys.exit(0)
    command = (data.get("tool_input") or {}).get("command", "")

    is_create, repo = parse_create(command)
    if not is_create:
        sys.exit(0)
    if repo is None:
        deny(MISSING_REPO)

    target = visibility(repo, None)
    if target is None or target[1] != "public":
        sys.exit(0)
    source = visibility(None, data.get("cwd"))
    if source is not None and source[1] != "public":
        deny(PRIVATE_TO_PUBLIC.format(source=source[0], target=target[0]))
    sys.exit(0)


if __name__ == "__main__":
    main()
