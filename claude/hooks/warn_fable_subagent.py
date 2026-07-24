#!/usr/bin/env python3
"""Soft-deny subagent invocations that would run on Fable.

Fires on ``PreToolUse`` events matched to the ``Agent`` tool. Denies
the call when the subagent would run on Fable, either via an explicit
``tool_input.model`` of ``"fable"``/``"claude-fable-5"``, or via
inheritance when ``model`` is unset and the session's
``ANTHROPIC_MODEL`` env var is a Fable alias.

``PreToolUse`` with matcher ``Agent`` was chosen over
``PermissionRequest``: the Agent tool was not observed to route
through the permission dialog in this session's harness (empirical,
not documented on the linked spec page), so ``PermissionRequest``
would not fire for it.

Exempt: subagent types whose ``~/.claude/agents/<subagent_type>.md``
frontmatter pins ``model: fable`` — mechanizes the "agents that pin
fable are exempt" clause of ``claude/rules/subagent-model.md``.

On the first denied occurrence of a given (subagent_type, effective
model) pair per session, the call is denied with a message steering
the caller toward an explicit ``"model": "sonnet"`` or ``"model":
"opus"``. Re-issuing the identical call (same subagent_type and
model) is let through on the second and later occurrences in the same
session, for cases where Fable really is required.

Session state is tracked in
``~/.claude/state/fable_subagent_warned_<session_id>.json``.
Set ``ENABLE_FABLE_SUBAGENT_WARNING=0`` to disable.

Spec: https://code.claude.com/docs/en/hooks#pretooluse
"""
import hashlib
import json
import os
import random
import re
import sys
from datetime import datetime

_STATE_DIR = os.path.expanduser("~/.claude/state")
_STATE_PREFIX = "fable_subagent_warned_"
_FABLE_ALIASES = frozenset({"fable", "claude-fable-5"})
_AGENTS_DIR = os.path.expanduser("~/.claude/agents")

_FRONTMATTER_MODEL_RE = re.compile(r"""^model:\s*['"]?(fable|claude-fable-5)['"]?\s*$""")

MESSAGE = (
    "Subagent would run on Fable (either explicit model=\"fable\" or inherited "
    "from session ANTHROPIC_MODEL=fable). Per claude/rules/subagent-model.md, "
    "subagents should default to sonnet (search / formatting / well-defined "
    "code) or opus (multi-file implementation / deep debugging / adversarial "
    "review). Retry with an explicit \"model\": \"sonnet\" or \"model\": "
    "\"opus\".\n\n"
    "If Fable is genuinely required for this specific subagent, re-issue the "
    "exact same Agent call (same subagent_type + model) — this hook lets the "
    "second occurrence in the same session through."
)


def _state_path(session_id: str) -> str:
    return os.path.join(_STATE_DIR, f"{_STATE_PREFIX}{session_id}.json")


def _load_state(session_id: str) -> set:
    try:
        with open(_state_path(session_id)) as f:
            return set(json.load(f))
    except (OSError, ValueError):
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


def _agent_pins_fable(subagent_type: str, agents_dir: str = _AGENTS_DIR) -> bool:
    """Return True if the agent's frontmatter pins model: fable.

    Reads ``<agents_dir>/<subagent_type>.md`` (defaults to
    ``~/.claude/agents/``) and checks whether the frontmatter block
    (delimited by ``---`` lines, starting at line 1) contains a
    ``model: fable`` (or ``claude-fable-5``) line. ``agents_dir`` is
    a doctest hook — production callers omit it.

    Rejects subagent_type values with path-traversal characters
    (``/`` or ``..``) before touching the filesystem:
    >>> _agent_pins_fable("../etc/passwd")
    False
    >>> _agent_pins_fable("nested/dir/name")
    False
    >>> _agent_pins_fable("")
    False

    Names without ``/`` or ``..`` fall through to file lookup and
    return False via the OSError branch when no matching file exists
    (e.g. missing agent, colon-qualified plugin names when
    ``~/.claude/agents/plugin:name.md`` isn't present):
    >>> _agent_pins_fable("does-not-exist-agent")
    False
    >>> _agent_pins_fable("plugin:name")
    False

    Agent frontmatter pins fable → exempt. Uses a tmpdir-injected
    ``agents_dir`` because CI never runs ``scripts/deploy.sh``, so
    ``~/.claude/agents/`` doesn't exist under the doctest job:
    >>> import tempfile
    >>> _tmpdir = tempfile.mkdtemp()
    >>> _ = open(os.path.join(_tmpdir, "fable-pinned.md"), "w").write(
    ...     "---\\nname: x\\nmodel: fable\\n---\\n")
    >>> _agent_pins_fable("fable-pinned", agents_dir=_tmpdir)
    True

    Same tmpdir, agent pins a non-fable model → not exempt (proves
    the loop inspects the value, not just the presence of ``model:``):
    >>> _ = open(os.path.join(_tmpdir, "opus-pinned.md"), "w").write(
    ...     "---\\nmodel: opus\\n---\\n")
    >>> _agent_pins_fable("opus-pinned", agents_dir=_tmpdir)
    False

    Alias ``claude-fable-5`` also counts as fable-pinned:
    >>> _ = open(os.path.join(_tmpdir, "cf5-pinned.md"), "w").write(
    ...     "---\\nmodel: claude-fable-5\\n---\\n")
    >>> _agent_pins_fable("cf5-pinned", agents_dir=_tmpdir)
    True
    """
    if not subagent_type or "/" in subagent_type or ".." in subagent_type:
        return False

    path = os.path.join(agents_dir, f"{subagent_type}.md")
    try:
        with open(path) as f:
            lines = f.readlines()
    except OSError:
        return False

    if not lines or lines[0].strip() != "---":
        return False

    for line in lines[1:]:
        stripped = line.rstrip("\n")
        if stripped.strip() == "---":
            break
        if _FRONTMATTER_MODEL_RE.match(stripped):
            return True
    return False


def _effective_model_is_fable(tool_input: dict) -> bool:
    """Return True if the subagent would effectively run on Fable.

    Explicit fable model:
    >>> _effective_model_is_fable({"model": "fable"})
    True

    Alias ``claude-fable-5`` also counts as Fable:
    >>> _effective_model_is_fable({"model": "claude-fable-5"})
    True

    Explicit non-fable model, regardless of session inheritance:
    >>> os.environ["ANTHROPIC_MODEL"] = "fable"
    >>> _effective_model_is_fable({"model": "sonnet"})
    False
    >>> del os.environ["ANTHROPIC_MODEL"]

    Unset model, inherits fable from session:
    >>> os.environ["ANTHROPIC_MODEL"] = "fable"
    >>> _effective_model_is_fable({})
    True
    >>> del os.environ["ANTHROPIC_MODEL"]

    Unset model, session is not fable:
    >>> _ = os.environ.pop("ANTHROPIC_MODEL", None)
    >>> _effective_model_is_fable({})
    False
    """
    model = tool_input.get("model")
    if model:
        return model in _FABLE_ALIASES
    return os.environ.get("ANTHROPIC_MODEL") in _FABLE_ALIASES


def _state_key(subagent_type: str, model: str) -> str:
    """Return a stable state key for a (subagent_type, model) pair.

    >>> _state_key("general-purpose", "fable") == _state_key("general-purpose", "fable")
    True
    >>> _state_key("general-purpose", "fable") == _state_key("general-purpose", "sonnet")
    False
    >>> _state_key("a", "fable") == _state_key("b", "fable")
    False
    """
    model_normalized = model or os.environ.get("ANTHROPIC_MODEL", "")
    normalized = f"{subagent_type}\x00{model_normalized}"
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()


def main() -> None:
    if os.environ.get("ENABLE_FABLE_SUBAGENT_WARNING", "1") == "0":
        sys.exit(0)

    if random.random() < 0.1:
        _cleanup_old_state()

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if data.get("tool_name") != "Agent":
        sys.exit(0)

    tool_input = data.get("tool_input") or {}

    if not _effective_model_is_fable(tool_input):
        sys.exit(0)

    subagent_type = tool_input.get("subagent_type", "")
    if subagent_type and _agent_pins_fable(subagent_type):
        sys.exit(0)

    session_id = data.get("session_id", "default")
    shown = _load_state(session_id)
    key = _state_key(subagent_type, tool_input.get("model", ""))

    if key not in shown:
        shown.add(key)
        if not _save_state(session_id, shown):
            # State didn't persist; skip the deny so the retry isn't
            # infinite. If the failure is persistent (unwritable state
            # dir, disk full), this branch fires on every Fable Agent
            # call — the hook silently no-ops until the I/O issue is
            # fixed.
            sys.exit(0)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": MESSAGE,
            },
        }))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
