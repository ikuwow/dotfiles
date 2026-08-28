#!/usr/bin/env python3
"""Stop hook: catch turns that promise work and then end without doing it.

Asks a Claude Haiku model whether the current turn committed to work
and then ended without starting it, given the turn's text and the tool
names it called. Silent no-op unless CLAUDE_STOP_CHECK_ANTHROPIC_API_KEY
is set.

On a YES verdict the hook writes to stderr and exits 2 — a contract
that works for both a synchronous Stop hook and one registered with
asyncRewake: true (see https://code.claude.com/docs/en/hooks). Whether
asyncRewake actually fires on a live Stop event is unverified; if it
does not, deleting that one settings.json flag needs no code change.

Every failure (stdin parse, transcript I/O, the API call, fire-count
state) is swallowed with a stderr breadcrumb and the hook exits 0
rather than wedging the turn.
"""
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request

from hook_utils import collect_current_turn_blocks

API_KEY_ENV = "CLAUDE_STOP_CHECK_ANTHROPIC_API_KEY"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 256
TIMEOUT_S = 8

POLL_INTERVAL_S = 0.05
POLL_MAX_ITERATIONS = 10

MAX_FIRINGS_PER_SESSION = 3

MUTATING_TOOL_NAMES = frozenset({"Edit", "Write", "NotebookEdit"})

VERDICT_SYSTEM_PROMPT = (
    "You judge whether an AI coding assistant's most recent turn committed "
    "to doing work and then ended the turn without starting it (an unkept "
    "promise). Answer NO for legitimate stops: the turn is waiting on user "
    "approval or an answer, the turn asked the user a question, the turn "
    "presented a plan for confirmation, the turn deliberately deferred and "
    "said so, or the turn is a pure explanation or answer with no work "
    "implied. Answer YES only when the turn states or implies it will do "
    "something and ends with no attempt to do it and no stated reason for "
    "deferring.\n\n"
    "Respond with exactly this format: a first line that is exactly YES or "
    "NO, then at most one more short line of justification."
)

REASON = (
    "This turn looks like it promised follow-up work and then ended "
    "without doing it or explaining why not.\n\n"
    "That judgment came from a Haiku classifier reading this turn's text "
    "and the names of the tools it called, not a keyword match — it can "
    "be wrong, including on turns that are legitimately waiting on you or "
    "the user, or that already stated a reason to defer.\n\n"
    "Judge your own turn: if you committed to doing something, do it now. "
    "If you are deliberately not doing it in this turn, say so explicitly."
)


def extract_tool_calls(blocks):
    """Return the names of tool_use blocks in blocks."""
    return [
        b.get("name", "") for b in blocks
        if isinstance(b, dict) and b.get("type") == "tool_use"
    ]


def is_mutating_turn(tool_names):
    """Return True if tool_names includes Edit, Write, or NotebookEdit.

    >>> is_mutating_turn(["Edit"])
    True
    >>> is_mutating_turn(["Read"])
    False
    """
    return any(name in MUTATING_TOOL_NAMES for name in tool_names)


def build_verdict_request(texts, tool_names):
    """Build the Messages API request body.

    Omits thinking/output_config.effort: Haiku 4.5 is extended-
    thinking-only (adaptive thinking type 400s on it) and Opus 4.5 is
    the only extended-thinking-only model that supports effort. See
    https://platform.claude.com/docs/en/build-with-claude/extended-thinking
    ("Migrating to adaptive thinking" and "Budget rules and tuning").
    """
    turn_text = "\n".join(texts)
    tools_line = ", ".join(tool_names) if tool_names else "(none)"
    user_content = f"Assistant turn text:\n{turn_text}\n\nTools called this turn: {tools_line}"
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": VERDICT_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_content}],
    }


def is_yes_verdict(response_json):
    """Return True only if the response's first content block is a clean YES.

    Any other shape — malformed, missing text, an off-contract reply —
    is treated as NO; a broken parse must never fire the hook.

    >>> is_yes_verdict({"content": [{"type": "text", "text": "YES\\nreason"}]})
    True
    >>> is_yes_verdict({"content": [{"type": "text", "text": "NO\\nreason"}]})
    False
    >>> is_yes_verdict({"content": [{"type": "text", "text": "YES-ish, unsure"}]})
    False
    >>> is_yes_verdict({"content": []})
    False
    >>> is_yes_verdict("not a dict")
    False
    """
    if not isinstance(response_json, dict):
        return False
    content = response_json.get("content")
    if not isinstance(content, list) or not content:
        return False
    first = content[0]
    text = first.get("text") if isinstance(first, dict) else None
    if not isinstance(text, str) or not text:
        return False
    first_line = text.strip().splitlines()[0].strip().upper()
    if first_line not in ("YES", "NO"):
        print(
            f"block_unkept_promise: verdict off-contract, treating as NO: {first_line!r}",
            file=sys.stderr,
        )
        return False
    return first_line == "YES"


def call_haiku_verdict(texts, tool_names, api_key):
    """Call the Messages API and return the boolean verdict; any failure is NO."""
    request_body = build_verdict_request(texts, tool_names)
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            response_json = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        print(f"block_unkept_promise: verdict call failed: {e!r} body={body!r}", file=sys.stderr)
        return False
    except Exception as e:  # broad on purpose: never wedge a turn on a broken API call
        print(f"block_unkept_promise: verdict call failed: {e!r}", file=sys.stderr)
        return False
    return is_yes_verdict(response_json)


def _state_file_path(session_id):
    """Sanitize session_id into a temp-dir file path, blocking path traversal.

    >>> _state_file_path("../../etc/passwd") == os.path.join(
    ...     tempfile.gettempdir(), "block_unkept_promise_______etc_passwd.count"
    ... )
    True
    """
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id) or "unknown"
    return os.path.join(tempfile.gettempdir(), f"block_unkept_promise_{safe_id}.count")


def _read_fire_count(session_id):
    """Return the session's fire count, or 0 on any read failure."""
    try:
        with open(_state_file_path(session_id), encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def record_fire(session_id):
    """Bump the session's fire count, written atomically via os.replace."""
    path = _state_file_path(session_id)
    count = _read_fire_count(session_id) + 1
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(str(count))
        os.replace(tmp_path, path)
    except OSError as e:
        print(f"block_unkept_promise: fire-count write failed: {e!r}", file=sys.stderr)
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def fire_cap_reached(session_id):
    """Return True once this session has fired MAX_FIRINGS_PER_SESSION times.

    Bounds an asyncRewake loop: each wake is a fresh turn, so
    stop_hook_active never sees a repeat there.
    """
    if not session_id:
        return False
    return _read_fire_count(session_id) >= MAX_FIRINGS_PER_SESSION


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_unkept_promise: stdin parse failed: {e!r}", file=sys.stderr)
        sys.exit(0)

    if not isinstance(data, dict):
        print(f"block_unkept_promise: stdin was not a JSON object: {data!r}", file=sys.stderr)
        sys.exit(0)

    if data.get("stop_hook_active"):
        sys.exit(0)

    # Checked before the transcript read so the disabled state costs
    # nothing: the poll loop below can otherwise spend POLL_INTERVAL_S *
    # POLL_MAX_ITERATIONS on every Stop for a hook that will never fire.
    api_key = os.environ.get(API_KEY_ENV, "")
    if not api_key:
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    if not transcript_path:
        print("block_unkept_promise: no transcript_path in stdin", file=sys.stderr)
        sys.exit(0)

    try:
        with open(transcript_path, encoding="utf-8") as f:
            events = [json.loads(line) for line in f if line.strip()]
    except (OSError, ValueError) as e:
        print(f"block_unkept_promise: transcript read failed: {e!r}", file=sys.stderr)
        sys.exit(0)

    # Reversed to chronological order: the classifier's question ("did
    # the turn end without doing the work it promised?") is positional,
    # and collect_current_turn_blocks returns most-recent-first.
    blocks = list(reversed(collect_current_turn_blocks(events)))
    texts = [b.get("text", "") for b in blocks if b.get("type") == "text"]

    if not texts:
        poll_start = time.monotonic()
        last_err = None
        for _ in range(POLL_MAX_ITERATIONS):
            time.sleep(POLL_INTERVAL_S)
            try:
                with open(transcript_path, encoding="utf-8") as f:
                    events = [json.loads(line) for line in f if line.strip()]
            except (OSError, ValueError) as e:
                last_err = e
                continue
            blocks = list(reversed(collect_current_turn_blocks(events)))
            texts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
            if texts:
                break

        if not texts:
            elapsed_ms = int((time.monotonic() - poll_start) * 1000)
            err_suffix = f" last_err={last_err!r}" if last_err else ""
            print(
                f"block_unkept_promise: poll timeout after {elapsed_ms}ms "
                f"events={len(events)} transcript={transcript_path}{err_suffix}",
                file=sys.stderr,
            )
            sys.exit(0)

    tool_names = extract_tool_calls(blocks)
    if is_mutating_turn(tool_names):
        sys.exit(0)

    session_id = data.get("session_id", "")
    if fire_cap_reached(session_id):
        sys.exit(0)

    if call_haiku_verdict(texts, tool_names, api_key):
        record_fire(session_id)
        print(REASON, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
