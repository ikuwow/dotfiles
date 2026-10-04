#!/usr/bin/env python3
"""Soft-deny the first gh publish command per session that targets a public destination.

Fires on ``PreToolUse`` events for ``Bash`` calls. When a command segment
is one of the outward-publishing gh commands below and its destination
is public, the first occurrence of that command per session is denied
with a message naming the destination, so the agent checks where the
text is about to land before it lands there. Re-issuing the same
command in the same session lets the hook fall through (``exit 0``).
Two commands are the same when they match after whitespace
normalization.

Publishing commands:

- ``gh issue create`` / ``gh pr create``
- ``gh issue edit`` / ``gh pr edit`` carrying a title or body flag
- ``gh issue comment`` / ``gh pr comment`` / ``gh pr review``
- ``gh release create``
- ``gh gist create`` with ``--public``/``-p`` (gists are secret by default)

The target repository comes from ``-R``/``--repo`` when present, and
otherwise from the repository gh resolves for the hook input's ``cwd``.
Visibility is read with ``gh api repos/<owner>/<repo>`` (REST).

The guard runs at ``PreToolUse`` because ``approve_git_gh_commands.py``
auto-approves ``gh pr create`` and ``gh issue create`` at the
``PermissionRequest`` stage, which a later-stage check could not
precede. It denies instead of returning ``"ask"`` because a hook-forced
prompt may itself reach that auto-approval.

Fail-open on every error (parse failure, gh error, timeout, state not
persisted): the hook exits 0 without a decision and prints one line to
stderr.

Registered under ``PreToolUse`` with ``matcher: "Bash"``. Session state
is tracked in ``~/.claude/state/public_publish_warned_<session_id>.json``.
Set ``ENABLE_PUBLIC_PUBLISH_GUARD=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#pretooluse
"""
import hashlib
import json
import os
import random
import re
import shlex
import subprocess
import sys
from datetime import datetime

_STATE_DIR = os.path.expanduser("~/.claude/state")
_STATE_PREFIX = "public_publish_warned_"
_SHELL_OPERATORS = frozenset({"&&", "||", "|", ";", "&", "\n"})
_ENV_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

_ALWAYS_PUBLISH = frozenset({
    ("issue", "create"),
    ("pr", "create"),
    ("issue", "comment"),
    ("pr", "comment"),
    ("pr", "review"),
    ("release", "create"),
})
_EDIT = frozenset({("issue", "edit"), ("pr", "edit")})
_EDIT_TEXT_FLAGS = frozenset({"--title", "-t", "--body", "-b", "--body-file", "-F"})
_REPO_FLAGS = frozenset({"--repo", "-R"})
_GIST_PUBLIC_FLAGS = frozenset({"--public", "-p"})

MESSAGE = (
    "This command publishes to {target}, which is PUBLIC. Before "
    "publishing, check whether any of the text (title, body, body file, "
    "comment, attached files) came from a private repository: its "
    "owner/name, issue or PR numbers, or source copied from it. If it "
    "did, stop and confirm with the user first. Otherwise re-run the "
    "exact same command; this session lets it through on the second and "
    "later occurrences (matched with whitespace normalized)."
)


def _segments(tokens):
    """Split tokens into command segments at shell operators.

    >>> _segments(["a", "&&", "b", "c", "|", "d"])
    [['a'], ['b', 'c'], ['d']]
    """
    segments = [[]]
    for tok in tokens:
        if tok in _SHELL_OPERATORS:
            segments.append([])
        else:
            segments[-1].append(tok)
    return [s for s in segments if s]


def _flag_value(args, flags):
    """Return the value of the first flag in ``flags``, or None.

    >>> _flag_value(["-R", "o/r", "--title", "x"], {"-R", "--repo"})
    'o/r'
    >>> _flag_value(["--repo=o/r"], {"-R", "--repo"})
    'o/r'
    >>> _flag_value(["--title", "x"], {"-R", "--repo"}) is None
    True
    """
    for i, tok in enumerate(args):
        flag, sep, inline_value = tok.partition("=")
        if flag in flags:
            if sep:
                return inline_value
            if i + 1 < len(args):
                return args[i + 1]
    return None


def _has_flag(args, flags):
    """Return True if any token is one of ``flags``, alone or ``=``-joined.

    >>> _has_flag(["--body-file=/tmp/x"], {"--body-file"})
    True
    >>> _has_flag(["--add-label", "x"], {"--body-file"})
    False
    """
    return any(tok.partition("=")[0] in flags for tok in args)


def parse_publish_command(command):
    """Return the first publishing gh command in ``command``, or None.

    The result is a dict with ``command`` (e.g. ``"issue create"``) and
    either ``repo`` (the ``-R``/``--repo`` value, or None for the cwd's
    repository) or ``gist: True`` for a public gist.

    >>> parse_publish_command("gh issue create -R ikuwow/dotfiles --title t --body b")
    {'command': 'issue create', 'repo': 'ikuwow/dotfiles'}
    >>> parse_publish_command("gh pr create --draft --body-file /tmp/b")
    {'command': 'pr create', 'repo': None}
    >>> parse_publish_command("gh pr comment 12 --repo=o/r -b hi")
    {'command': 'pr comment', 'repo': 'o/r'}
    >>> parse_publish_command("gh release create v1 -R o/r --notes n")
    {'command': 'release create', 'repo': 'o/r'}

    Edits fire only when they change the title or body:

    >>> parse_publish_command("gh pr edit 3 --body-file /tmp/b")
    {'command': 'pr edit', 'repo': None}
    >>> parse_publish_command("gh issue edit 3 --add-label bug") is None
    True

    Gists fire only when public:

    >>> parse_publish_command("gh gist create --public notes.md")
    {'command': 'gist create', 'gist': True}
    >>> parse_publish_command("gh gist create notes.md") is None
    True

    A publishing segment after a shell operator or an env assignment
    still counts:

    >>> parse_publish_command("git push -u origin HEAD && gh pr create --draft")
    {'command': 'pr create', 'repo': None}
    >>> parse_publish_command("GH_PAGER= gh issue comment 5 -b x")
    {'command': 'issue comment', 'repo': None}

    Non-publishing and unparseable commands return None:

    >>> parse_publish_command("gh pr view 3 --comments") is None
    True
    >>> parse_publish_command("git commit -m 'gh issue create'") is None
    True
    >>> parse_publish_command("gh issue create --title 'unterminated") is None
    True
    """
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    for segment in _segments(tokens):
        while segment and _ENV_ASSIGNMENT_RE.match(segment[0]):
            segment = segment[1:]
        if len(segment) < 3 or segment[0] != "gh":
            continue
        pair = (segment[1], segment[2])
        args = segment[3:]
        name = f"{pair[0]} {pair[1]}"
        if pair == ("gist", "create"):
            if _has_flag(args, _GIST_PUBLIC_FLAGS):
                return {"command": name, "gist": True}
            continue
        if pair in _ALWAYS_PUBLISH or (
            pair in _EDIT and _has_flag(args, _EDIT_TEXT_FLAGS)
        ):
            return {"command": name, "repo": _flag_value(args, _REPO_FLAGS)}
    return None


def _repo_api_args(repo):
    """Return the ``gh api`` arguments that fetch ``repo``'s metadata.

    >>> _repo_api_args(None)
    ['repos/{owner}/{repo}']
    >>> _repo_api_args("o/r")
    ['repos/o/r']
    >>> _repo_api_args("github.example.com/o/r")
    ['--hostname', 'github.example.com', 'repos/o/r']
    """
    if repo is None:
        return ["repos/{owner}/{repo}"]
    parts = repo.split("/")
    if len(parts) == 3:
        return ["--hostname", parts[0], f"repos/{parts[1]}/{parts[2]}"]
    return [f"repos/{repo}"]


def _resolve_visibility(repo, cwd):
    """Return (full_name, visibility) for the target repo, or None on error."""
    cmd = ["gh", "api", *_repo_api_args(repo), "--jq", "[.full_name, .visibility] | join(\" \")"]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15, check=False,
            cwd=cwd or None,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"guard_public_publish: gh api failed: {e}", file=sys.stderr)
        return None
    if proc.returncode != 0:
        print(f"guard_public_publish: gh api exited {proc.returncode}", file=sys.stderr)
        return None
    parts = proc.stdout.split()
    if len(parts) != 2:
        print("guard_public_publish: unexpected gh api output", file=sys.stderr)
        return None
    return parts[0], parts[1]


def _command_key(command: str) -> str:
    """Return a stable state key for a command, normalizing whitespace.

    >>> _command_key("gh pr create") == _command_key(" gh  pr create ")
    True
    >>> _command_key("gh pr create") == _command_key("gh issue create")
    False
    """
    normalized = re.sub(r"\s+", " ", command).strip()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def _state_path(session_id: str) -> str:
    return os.path.join(_STATE_DIR, f"{_STATE_PREFIX}{session_id}.json")


def _load_state(session_id: str) -> set:
    try:
        with open(_state_path(session_id)) as f:
            return set(json.load(f))
    except (OSError, ValueError, TypeError):
        return set()


def _save_state(session_id: str, shown: set) -> bool:
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
        with open(_state_path(session_id), "w") as f:
            json.dump(sorted(shown), f)
    except OSError:
        return False
    return True


def _cleanup_old_state() -> None:
    try:
        if not os.path.isdir(_STATE_DIR):
            return
        cutoff = datetime.now().timestamp() - 30 * 24 * 60 * 60
        for name in os.listdir(_STATE_DIR):
            if not name.startswith(_STATE_PREFIX) or not name.endswith(".json"):
                continue
            path = os.path.join(_STATE_DIR, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except OSError:
                pass
    except OSError:
        pass


def main() -> None:
    if os.environ.get("ENABLE_PUBLIC_PUBLISH_GUARD", "1") == "0":
        sys.exit(0)

    if random.random() < 0.1:
        _cleanup_old_state()

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    if not isinstance(data, dict) or data.get("tool_name", "") != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        sys.exit(0)
    command = tool_input.get("command", "")
    if not command:
        sys.exit(0)

    parsed = parse_publish_command(command)
    if parsed is None:
        sys.exit(0)

    session_id = data.get("session_id", "default")
    shown = _load_state(session_id)
    key = _command_key(command)
    if key in shown:
        sys.exit(0)

    if parsed.get("gist"):
        target = "a public gist"
    else:
        resolved = _resolve_visibility(parsed["repo"], data.get("cwd"))
        if resolved is None:
            sys.exit(0)
        full_name, visibility = resolved
        if visibility != "public":
            sys.exit(0)
        target = full_name

    shown.add(key)
    if not _save_state(session_id, shown):
        # State didn't persist; skip the deny so the retry isn't infinite.
        print("guard_public_publish: could not persist state", file=sys.stderr)
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": MESSAGE.format(target=target),
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
