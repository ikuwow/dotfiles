#!/usr/bin/env python3
"""Warn on Bash invocations of ``gh api`` in favor of high-level ``gh`` subcommands.

Detects ``gh api ...`` (including ``gh api graphql ...``) in Bash commands.
On the first occurrence per session per distinct command, denies the tool
call with a suggestion to prefer high-level ``gh`` subcommands (``gh pr
view``, ``gh pr diff``, ``gh pr checks``, ``gh issue view --comments``,
``gh run view``, the ``gh pr-review`` extension for PR review threads).
Re-issuing the exact same command in the same session is allowed through
so the assistant can proceed after confirming ``gh api`` is actually
needed. Two commands are considered the same when they match after
whitespace normalization (leading/trailing trim, internal runs of
whitespace collapsed to a single space).

Session state is tracked in ``~/.claude/state/gh_api_warned_<session_id>.json``.
Set ``ENABLE_GH_API_WARNING=0`` to disable.

Commands where every ``gh api`` segment is a read of the contents endpoint
(``gh api repos/OWNER/REPO/contents/PATH``, no write flags) are allowlisted
and pass through without a deny on the first occurrence.

Spec: https://docs.anthropic.com/en/docs/claude-code/hooks
"""
import hashlib
import json
import os
import random
import re
import shlex
import sys
from datetime import datetime

# Split on &&, ||, ;, newline, or single | (pipe) outside quotes.
# `\|\|` is tried before `\|` so `||` is not consumed as two `|`.
_SEPARATOR_RE = re.compile(r"&&|\|\||;|\n|\|")

_STATE_DIR = os.path.expanduser("~/.claude/state")
_STATE_PREFIX = "gh_api_warned_"

REASON = (
    "Detected 'gh api'. Prefer high-level gh subcommands first:\n"
    "  gh pr view / gh pr diff / gh pr checks\n"
    "  gh issue view (with --comments)\n"
    "  gh run view\n"
    "  gh pr-review (extension: agynio/gh-pr-review) for PR review threads\n"
    "Fall back to 'gh api' / 'gh api graphql' only when the high-level "
    "subcommands cannot express the operation. If that is the case, "
    "re-run the exact same command as-is — this session lets it through "
    "on the second and later occurrences of the same command (matched "
    "with whitespace normalized)."
)


def _split_outside_quotes(command: str) -> list[str]:
    """Split command by shell separators, ignoring separators inside quotes.

    >>> _split_outside_quotes("cat file | gh api foo")
    ['cat file ', ' gh api foo']
    >>> _split_outside_quotes("echo 'gh api hi | more'")
    ["echo 'gh api hi | more'"]
    >>> _split_outside_quotes("a && b || c ; d")
    ['a ', ' b ', ' c ', ' d']
    >>> _split_outside_quotes("a\\ngh api x")
    ['a', 'gh api x']
    >>> _split_outside_quotes('echo "pipe | inside double"')
    ['echo "pipe | inside double"']
    """
    segments = []
    current = []
    in_single = False
    in_double = False
    i = 0
    while i < len(command):
        ch = command[i]

        if ch == "\\" and in_double and i + 1 < len(command):
            current.append(ch)
            current.append(command[i + 1])
            i += 2
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
            i += 1
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
            i += 1
            continue

        if not in_single and not in_double:
            match = _SEPARATOR_RE.match(command, i)
            if match:
                segments.append("".join(current))
                current = []
                i = match.end()
                continue

        current.append(ch)
        i += 1

    segments.append("".join(current))
    return segments


def detect_gh_api(command: str) -> bool:
    """Return True if a shell segment invokes ``gh api`` (or ``gh api graphql``).

    Detected — plain ``gh api``:
    >>> detect_gh_api("gh api repos/foo/bar/pulls/123")
    True
    >>> detect_gh_api("gh api graphql -f query='...'")
    True
    >>> detect_gh_api('gh api -H "Accept: application/vnd.github.raw" repos/foo/bar')
    True

    Detected — after a pipe, ``&&``, ``;``, or newline:
    >>> detect_gh_api("something | gh api foo")
    True
    >>> detect_gh_api("mkdir d && gh api foo")
    True
    >>> detect_gh_api("ls ; gh api foo")
    True
    >>> detect_gh_api("mkdir d\\ngh api foo")
    True

    NOT detected — high-level gh subcommands:
    >>> detect_gh_api("gh pr view 123")
    False
    >>> detect_gh_api("gh issue view 5 --comments")
    False

    NOT detected — inside quotes, or as a substring/argument:
    >>> detect_gh_api('echo "gh api hello"')
    False
    >>> detect_gh_api("git commit -m 'switch from gh api to gh pr view'")
    False
    >>> detect_gh_api("github-api something")
    False
    >>> detect_gh_api("gh api-helper foo")
    False

    NOT detected — empty string:
    >>> detect_gh_api("")
    False
    """
    for seg in _split_outside_quotes(command):
        seg = seg.strip()
        if not seg:
            continue
        if not re.match(r"gh(\s|$)", seg):
            continue
        tokens = seg.split()
        if len(tokens) < 2:
            continue
        for token in tokens[1:]:
            if token.startswith("-"):
                continue
            if token == "api":
                return True
            break
    return False


_CONTENTS_RE = re.compile(r"repos/[^/\s]+/[^/\s]+/contents/[^\s]+")
_WRITE_FLAGS = {"-X", "--method", "-f", "--field", "-F", "--raw-field", "--input"}


def is_contents_read(command: str) -> bool:
    """Return True if every ``gh api`` segment is a read of the contents endpoint.

    Detected — plain contents read:
    >>> is_contents_read("gh api repos/foo/bar/contents/README.md")
    True
    >>> is_contents_read(
    ...     'gh api repos/foo/bar/contents/path/to/file.py -H '
    ...     '"Accept: application/vnd.github.raw"'
    ... )
    True
    >>> is_contents_read("gh api repos/foo/bar/contents/README.md?ref=trunk")
    True

    NOT detected — non-contents endpoint, or graphql:
    >>> is_contents_read("gh api repos/foo/bar/pulls/123")
    False
    >>> is_contents_read("gh api graphql -f query='...'")
    False

    NOT detected — write flags present:
    >>> is_contents_read(
    ...     "gh api repos/foo/bar/contents/x.md -X PUT "
    ...     "-f message=... -f content=..."
    ... )
    False
    >>> is_contents_read("gh api repos/foo/bar/contents/x.md -f sha=abc")
    False

    NOT detected — not a gh api command at all, or empty:
    >>> is_contents_read("gh pr view 123")
    False
    >>> is_contents_read("")
    False

    Compound commands — every gh api segment must qualify:
    >>> is_contents_read("mkdir d && gh api repos/foo/bar/contents/README.md")
    True
    >>> is_contents_read(
    ...     "gh api repos/foo/bar/contents/README.md && "
    ...     "gh api repos/foo/bar/pulls/1"
    ... )
    False
    """
    found_gh_api = False
    for seg in _split_outside_quotes(command):
        seg = seg.strip()
        if not seg:
            continue
        if not re.match(r"gh(\s|$)", seg):
            continue
        try:
            tokens = shlex.split(seg)
        except ValueError:
            return False
        if len(tokens) < 2:
            continue

        api_index = None
        for idx, token in enumerate(tokens[1:], start=1):
            if token.startswith("-"):
                continue
            if token == "api":
                api_index = idx
            break
        if api_index is None:
            continue

        found_gh_api = True
        rest = tokens[api_index + 1:]
        if any(tok in _WRITE_FLAGS for tok in rest):
            return False
        if not any(_CONTENTS_RE.fullmatch(tok) for tok in rest):
            return False

    return found_gh_api


def _state_path(session_id: str) -> str:
    return os.path.join(_STATE_DIR, f"{_STATE_PREFIX}{session_id}.json")


def _load_state(session_id: str) -> set:
    try:
        with open(_state_path(session_id)) as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def _save_state(session_id: str, shown: set) -> None:
    try:
        os.makedirs(_STATE_DIR, exist_ok=True)
        with open(_state_path(session_id), "w") as f:
            json.dump(sorted(shown), f)
    except OSError:
        pass


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


def _command_key(command: str) -> str:
    """Return a stable state key for a command, normalizing whitespace.

    >>> _command_key("gh api foo") == _command_key("gh  api  foo")
    True
    >>> _command_key("gh api foo") == _command_key(" gh api foo ")
    True
    >>> _command_key("gh api foo") == _command_key("gh api bar")
    False
    """
    normalized = re.sub(r"\s+", " ", command).strip()
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def main() -> None:
    if os.environ.get("ENABLE_GH_API_WARNING", "1") == "0":
        sys.exit(0)

    if random.random() < 0.1:
        _cleanup_old_state()

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name", "") != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    if not detect_gh_api(command):
        sys.exit(0)

    if is_contents_read(command):
        sys.exit(0)

    session_id = data.get("session_id", "default")
    shown = _load_state(session_id)
    key = _command_key(command)

    if key not in shown:
        shown.add(key)
        _save_state(session_id, shown)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": REASON,
            },
        }))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
