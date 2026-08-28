#!/usr/bin/env python3
"""Stop hook: catch turns that promise work and then end without doing it.

Phrasing like "やっておくよ", "あとで直しとく", or "I'll handle that" spans
an open-ended space that a fixed phrase list cannot cover and would need
endless maintenance. Instead of matching text, this hook asks a Claude
Haiku model to judge whether the current turn committed to work and then
ended without starting it, given the turn's text and the names of the
tools it called.

Most turns that actually do work call a mutating tool (Edit, Write,
NotebookEdit, or a non-read-only Bash command), so the prefilter in
is_mutating_turn() exits before any API call runs — this is the whole
latency story: ordinary working turns never pay for a network round
trip. Only turns with no mutating tool call reach the Haiku call.

On a YES verdict the hook writes to stderr and exits 2. Per
https://code.claude.com/docs/en/hooks this is a single contract that
works for both a synchronous Stop hook (exit 2 blocks the stop and
Claude reads the reason from stderr) and one registered with
asyncRewake: true (exit 2 wakes Claude, with stderr — or stdout if
stderr is empty — shown as a system reminder). Whether asyncRewake
actually fires on the Stop event is unverified; if it does not, the
fallback is deleting that one settings.json flag with no code change.

stop_hook_active guards the synchronous Stop chain, but an asyncRewake
wake starts a fresh turn, so that flag alone cannot stop a wake loop.
already_fired()/record_fired() add a second guard keyed on the uuid of
the assistant message the hook fired on, persisted under
tempfile.gettempdir() per session_id.

I/O failures (stdin parse, missing transcript_path, transcript read,
poll timeout) and API failures (network, timeout, malformed JSON,
missing field, unparseable verdict) are all swallowed and the hook
exits 0 — a Stop hook that wedges the assistant is far worse than one
that silently no-ops. A short stderr breadcrumb is emitted on each
terminal fall-through so the operator can grep hook logs and tell
"rule not satisfied" apart from "hook silently broken". The one
exception is the opt-in env var being unset: that is the hook's normal
disabled state and is silent by design.

For pure-text turns (no tool calls), Claude Code can invoke the Stop
hook before the assistant event is flushed to the transcript JSONL.
When the initial read returns no current-turn assistant text, the hook
polls the transcript at POLL_INTERVAL_S intervals up to
POLL_MAX_ITERATIONS iterations before giving up fail-open, mirroring
block_excuse_phrases.py.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import os
import re
import sys
import tempfile
import time
import urllib.request

from hook_utils import collect_current_turn_blocks

API_KEY_ENV = "CLAUDE_STOP_CHECK_ANTHROPIC_API_KEY"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 256
TIMEOUT_S = 8

POLL_INTERVAL_S = 0.05
POLL_MAX_ITERATIONS = 10

MUTATING_TOOL_NAMES = frozenset({"Edit", "Write", "NotebookEdit"})

# Bare commands that are read-only regardless of arguments, for the
# purposes of this prefilter (redirection/xargs tricks are out of
# scope — see is_readonly_bash_command).
READONLY_BARE_COMMANDS = frozenset(
    {"cat", "head", "tail", "grep", "rg", "ls", "find", "wc", "jq", "yq", "which", "echo"}
)

# A single "|" that is not part of "||". Quoting is not modeled — see
# module note on keeping the Bash classifier simple.
_PIPE_RE = re.compile(r"(?<!\|)\|(?!\|)")

# An output redirect and its target. The target charset excludes "&" so
# that fd duplications like "2>&1" yield no match and stay read-only.
_REDIRECT_RE = re.compile(r">>?\s*([^\s|&]+)")

# The one redirect target that writes nothing.
_NULL_SINK = "/dev/null"

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


def _pipeline_segments(command):
    return [seg.strip() for seg in _PIPE_RE.split(command)]


def _is_segment_readonly(segment):
    # A redirect makes any segment a write, whatever the command name.
    # This is what keeps heredoc file writes ("cat > f <<EOF") from
    # passing as read-only on the strength of "cat" alone.
    if any(
        target != _NULL_SINK for target in _REDIRECT_RE.findall(segment)
    ):
        return False
    tokens = segment.split()
    if not tokens:
        return True
    first = tokens[0]
    second = tokens[1] if len(tokens) > 1 else ""
    if first in READONLY_BARE_COMMANDS:
        return True
    if first == "sed":
        return "-n" in tokens[1:]
    if first == "command":
        return second == "-v"
    if first == "git":
        return second in {"status", "log", "diff", "show", "branch"}
    if first == "gh":
        third = tokens[2] if len(tokens) > 2 else ""
        if second == "pr" and third in {"view", "checks"}:
            return True
        if second == "issue" and third == "view":
            return True
        return False
    return False


def is_readonly_bash_command(command):
    """Return True if every segment of a Bash pipeline is recognizably read-only.

    Unrecognized commands are treated as mutating — this is an
    allowlist, not a blocklist, so the default for anything not
    explicitly named below is "mutating" (erring toward not blocking).

    Recognized read-only commands:

    >>> is_readonly_bash_command("cat foo.txt")
    True
    >>> is_readonly_bash_command("head -n 5 file")
    True
    >>> is_readonly_bash_command("sed -n '1,5p' file")
    True
    >>> is_readonly_bash_command("git status")
    True
    >>> is_readonly_bash_command("git diff HEAD~1")
    True
    >>> is_readonly_bash_command("gh pr view 123")
    True
    >>> is_readonly_bash_command("gh pr checks 123")
    True
    >>> is_readonly_bash_command("gh issue view 5")
    True
    >>> is_readonly_bash_command("command -v python3")
    True
    >>> is_readonly_bash_command("which python3")
    True

    A pipeline is read-only only when every segment is:

    >>> is_readonly_bash_command("ls -la | wc -l")
    True
    >>> is_readonly_bash_command("cat file.txt | tee out.txt")
    False

    Mutating commands, including a read-only command name used in a
    mutating way:

    >>> is_readonly_bash_command("sed -i 's/a/b/' file")
    False
    >>> is_readonly_bash_command("git commit -am 'x'")
    False
    >>> is_readonly_bash_command("gh pr merge 123")
    False
    >>> is_readonly_bash_command("rm -rf /tmp/x")
    False

    Unrecognized commands default to mutating:

    >>> is_readonly_bash_command("some-unknown-tool --flag")
    False

    A redirect makes the segment a write even when the command name is
    on the allowlist, which covers the heredoc file-write idiom:

    >>> is_readonly_bash_command("cat > out.txt <<EOF")
    False
    >>> is_readonly_bash_command("echo hi >> log.txt")
    False

    Redirects that write nothing stay read-only:

    >>> is_readonly_bash_command("grep -r foo . 2>/dev/null")
    True
    >>> is_readonly_bash_command("ls missing 2>&1")
    True

    An empty command is vacuously read-only (no segment to fail):

    >>> is_readonly_bash_command("")
    True
    """
    if not command:
        return True
    return all(_is_segment_readonly(seg) for seg in _pipeline_segments(command))


def extract_tool_calls(blocks):
    """Extract (name, command) tuples from tool_use blocks.

    command is populated only for Bash tool calls; every other tool
    gets None since the prefilter only needs the command text for Bash.

    >>> extract_tool_calls([
    ...     {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
    ... ])
    [('Bash', 'ls')]
    >>> extract_tool_calls([{"type": "tool_use", "name": "Edit", "input": {"file_path": "x"}}])
    [('Edit', None)]
    >>> extract_tool_calls([{"type": "text", "text": "hi"}])
    []
    >>> extract_tool_calls([])
    []
    """
    calls = []
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        name = block.get("name", "")
        command = None
        if name == "Bash":
            command = block.get("input", {}).get("command")
        calls.append((name, command))
    return calls


def is_mutating_turn(tool_calls):
    """Return True if a tool call in tool_calls shows the turn already did work.

    When this is True the hook skips the Haiku call entirely: ordinary
    working turns edit something, so they never pay for the network
    round trip.

    >>> is_mutating_turn([("Edit", None)])
    True
    >>> is_mutating_turn([("Write", None)])
    True
    >>> is_mutating_turn([("NotebookEdit", None)])
    True
    >>> is_mutating_turn([("Bash", "git commit -am 'x'")])
    True
    >>> is_mutating_turn([("Bash", "git status")])
    False
    >>> is_mutating_turn([("Read", None)])
    False
    >>> is_mutating_turn([])
    False
    """
    for name, command in tool_calls:
        if name in MUTATING_TOOL_NAMES:
            return True
        if name == "Bash" and not is_readonly_bash_command(command or ""):
            return True
    return False


def build_verdict_request(texts, tool_names):
    """Build the Messages API request body for the verdict call.

    Sends only the current turn's assistant text and tool names — no
    tool inputs or results — to keep token cost down and file contents
    off the wire. No thinking/output_config.effort field is sent:
    Haiku 4.5 predates adaptive thinking and effort errors on it.

    >>> req = build_verdict_request(["I'll fix that next."], ["Read"])
    >>> req["model"]
    'claude-haiku-4-5'
    >>> req["max_tokens"]
    256
    >>> "thinking" in req
    False
    >>> "output_config" in req
    False
    >>> "I'll fix that next." in req["messages"][0]["content"]
    True
    >>> "Read" in req["messages"][0]["content"]
    True
    >>> build_verdict_request([], [])["messages"][0]["content"]
    'Assistant turn text:\\n\\n\\nTools called this turn: (none)'
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


def extract_verdict_text(response_json):
    """Pull the model's reply text out of a Messages API response body.

    >>> extract_verdict_text({"content": [{"type": "text", "text": "YES\\nreason"}]})
    'YES\\nreason'
    >>> extract_verdict_text({"content": []}) is None
    True
    >>> extract_verdict_text({}) is None
    True
    >>> extract_verdict_text({"content": [{"type": "text"}]}) is None
    True
    >>> extract_verdict_text("not a dict") is None
    True
    """
    if not isinstance(response_json, dict):
        return None
    content = response_json.get("content")
    if not isinstance(content, list) or not content:
        return None
    first = content[0]
    if not isinstance(first, dict):
        return None
    text = first.get("text")
    return text if isinstance(text, str) else None


def parse_verdict(text):
    """Parse the model's reply text into a strict boolean verdict.

    Anything that does not parse as a clean YES on the first line is
    treated as NO — a malformed or ambiguous reply must never fire the
    hook.

    >>> parse_verdict("YES\\nturn promised a fix and stopped")
    True
    >>> parse_verdict("NO\\nturn is waiting on user confirmation")
    False
    >>> parse_verdict("yes")
    True
    >>> parse_verdict("YES-ish, hard to tell")
    False
    >>> parse_verdict("")
    False
    >>> parse_verdict(None)
    False
    """
    if not text:
        return False
    first_line = text.strip().splitlines()[0].strip()
    return first_line.upper() == "YES"


def call_haiku_verdict(texts, tool_names, api_key):
    """Call the Anthropic Messages API and return the boolean verdict.

    Any failure — network, timeout, malformed JSON, missing field, or
    an unparseable verdict — is swallowed and treated as NO with a
    stderr breadcrumb. Broad exception handling here is deliberate: a
    Stop hook must never wedge a turn on a broken API call.
    """
    request_body = build_verdict_request(texts, tool_names)
    try:
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
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            response_json = json.loads(resp.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001 - see docstring
        print(f"block_unkept_promise: verdict call failed: {e}", file=sys.stderr)
        return False

    verdict_text = extract_verdict_text(response_json)
    if verdict_text is None:
        print("block_unkept_promise: verdict response missing text", file=sys.stderr)
        return False
    return parse_verdict(verdict_text)


def latest_assistant_uuid(events):
    """Return the uuid of the most recent assistant event, or None.

    >>> latest_assistant_uuid([
    ...     {"type": "assistant", "uuid": "a1", "message": {"content": []}},
    ...     {"type": "user", "uuid": "u1", "message": {"content": "hi"}},
    ... ])
    'a1'
    >>> latest_assistant_uuid([{"type": "user", "message": {}}]) is None
    True
    >>> latest_assistant_uuid([]) is None
    True
    """
    for event in reversed(events):
        if event.get("type") == "assistant":
            return event.get("uuid")
    return None


def _state_file_path(session_id):
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id) or "unknown"
    return os.path.join(tempfile.gettempdir(), f"block_unkept_promise_{safe_id}.json")


def already_fired(session_id, uuid):
    """Return True if this hook already fired on this assistant message uuid.

    Guards the asyncRewake loop: a rewake starts a fresh turn, so
    stop_hook_active alone cannot stop repeated firing on the same
    underlying message. Read failures are swallowed and treated as
    "not fired yet" rather than raising.
    """
    if not session_id or not uuid:
        return False
    try:
        with open(_state_file_path(session_id), encoding="utf-8") as f:
            state = json.load(f)
        return state.get("last_fired_uuid") == uuid
    except (OSError, json.JSONDecodeError, ValueError):
        return False


def record_fired(session_id, uuid):
    """Persist the uuid this hook just fired on. Write failures are non-fatal."""
    if not session_id or not uuid:
        return
    try:
        with open(_state_file_path(session_id), "w", encoding="utf-8") as f:
            json.dump({"last_fired_uuid": uuid}, f)
    except OSError:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_unkept_promise: stdin parse failed: {e}", file=sys.stderr)
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
    except (OSError, json.JSONDecodeError) as e:
        print(f"block_unkept_promise: transcript read failed: {e}", file=sys.stderr)
        sys.exit(0)

    blocks = collect_current_turn_blocks(events)
    texts = [b.get("text", "") for b in blocks if b.get("type") == "text"]

    if not texts:
        poll_start = time.monotonic()
        last_err = None
        for _ in range(POLL_MAX_ITERATIONS):
            time.sleep(POLL_INTERVAL_S)
            try:
                with open(transcript_path, encoding="utf-8") as f:
                    events = [json.loads(line) for line in f if line.strip()]
            except (OSError, json.JSONDecodeError) as e:
                last_err = e
                continue
            blocks = collect_current_turn_blocks(events)
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

    tool_calls = extract_tool_calls(blocks)
    if is_mutating_turn(tool_calls):
        sys.exit(0)

    session_id = data.get("session_id", "")
    current_uuid = latest_assistant_uuid(events)
    if already_fired(session_id, current_uuid):
        sys.exit(0)

    tool_names = [name for name, _ in tool_calls]
    if call_haiku_verdict(texts, tool_names, api_key):
        record_fired(session_id, current_uuid)
        print(REASON, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
