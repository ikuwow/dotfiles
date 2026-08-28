#!/usr/bin/env python3
"""Stop hook: catch turns that promise work and then end without doing it.

This hook asks a Claude Haiku model to judge whether the current turn
committed to work and then ended without starting it, given the turn's
text and the names of the tools it called.

Most turns that actually do work call a mutating tool (Edit, Write,
NotebookEdit, or a non-read-only Bash command), so the prefilter in
is_mutating_turn() exits before any API call runs, removing the
network round trip for ordinary working turns. The poll loop described
below still runs ahead of that prefilter for pure-text turns, so the
prefilter is only the network half of the hook's latency, not the
whole of it.

On a YES verdict the hook writes to stderr and exits 2. Per
https://code.claude.com/docs/en/hooks this is a single contract that
works for both a synchronous Stop hook (exit 2 blocks the stop and
Claude reads the reason from stderr) and one registered with
asyncRewake: true (exit 2 wakes Claude, with stderr — or stdout if
stderr is empty — shown as a system reminder). The installed Claude
Code binary's own config schema documents that general mechanism in
those terms, including a default wake-message label of "Stop hook
feedback" that suggests it targets this event; what remains unverified
in this session is not that documented mechanism but whether it
actually fires end to end on a live Stop event. If it does not, the
fallback is deleting that one settings.json flag with no code change.

stop_hook_active guards the synchronous Stop chain, but an asyncRewake
wake starts a fresh turn with a new assistant message uuid, so that
flag alone cannot stop a wake loop. already_fired()/record_fired() add
a second guard in a per-session state file with two independent
bounds: the uuid bound enforces at most one firing per assistant
message, and the fire-count bound caps firings per session at
MAX_FIRINGS_PER_SESSION. Only the fire-count bound actually stops a
wake loop, since each wake carries a uuid the uuid bound has never
seen.

I/O failures (stdin parse, missing transcript_path, transcript read,
poll timeout) and API failures (network, timeout, malformed JSON,
missing field, unparseable verdict) are all swallowed and the hook
exits 0 — a Stop hook that wedges the assistant is far worse than one
that silently no-ops. Every one of these failure fall-throughs emits a
stderr breadcrumb so an operator can grep hook logs and tell "rule not
satisfied" apart from "hook silently broken", except the opt-in env
var being unset, which is the hook's normal disabled state and is
silent by design. Other deliberate no-op exits — stop_hook_active, the
mutating-tool prefilter, the already_fired guard, and a NO verdict —
are ordinary early returns, not failures, and are silent for that
reason rather than following the breadcrumb convention above.

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
import urllib.error
import urllib.request

from hook_utils import collect_current_turn_blocks, has_unsafe_substitution, split_outside_quotes

API_KEY_ENV = "CLAUDE_STOP_CHECK_ANTHROPIC_API_KEY"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 256
TIMEOUT_S = 8

POLL_INTERVAL_S = 0.05
POLL_MAX_ITERATIONS = 10

MAX_FIRINGS_PER_SESSION = 3

MUTATING_TOOL_NAMES = frozenset({"Edit", "Write", "NotebookEdit"})

# Bare commands that are read-only regardless of arguments. find, git
# branch, and yq are deliberately excluded here and gated separately
# below because each has a common invocation that mutates (find
# -delete/-exec, git branch -D, yq -i). Genuinely unmodeled: a command
# reached through xargs, eval, a shell function, or an alias — this
# classifier only ever looks at the first token of a segment, so a
# command name hidden behind any of those is invisible to it.
READONLY_BARE_COMMANDS = frozenset(
    {"cat", "head", "tail", "grep", "rg", "ls", "wc", "jq", "which", "echo"}
)

_GIT_READONLY_SUBCOMMANDS = {"status", "log", "diff", "show"}
_GIT_BRANCH_MUTATING_FLAGS = {"-d", "-D", "-m", "-M", "-c", "-C", "--delete", "--move", "--copy"}
_FIND_MUTATING_FLAGS = {
    "-delete", "-exec", "-execdir", "-ok", "-okdir",
    "-fprint", "-fprint0", "-fprintf", "-fls",
}
_YQ_MUTATING_FLAGS = {"-i", "--inplace"}

# An output redirect and its target. The target charset excludes "&" so
# that fd duplications like "2>&1" yield no match and stay read-only.
_REDIRECT_RE = re.compile(r">>?\s*([^\s|&]+)")

# The one redirect target that writes nothing.
_NULL_SINK = "/dev/null"

# fd duplication ("2>&1", "1>&2") contains a bare "&" that
# hook_utils.split_outside_quotes otherwise reads as a backgrounding
# separator (correctly, for its other caller — block_aws_logs_start_
# query.py needs "cmd &" to split there). Masking the "&" in this one
# idiom before splitting, then restoring it per segment afterward,
# keeps the fd-dup target intact for _REDIRECT_RE without changing the
# shared splitter's general behavior.
_FD_DUP_RE = re.compile(r"\d*>&\d+")
_FD_DUP_PLACEHOLDER = "\x00"

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


def _is_git_branch_readonly(rest):
    if any(t in _GIT_BRANCH_MUTATING_FLAGS for t in rest):
        return False
    return not any(not t.startswith("-") for t in rest)


def _mask_fd_dup(command):
    return _FD_DUP_RE.sub(lambda m: m.group(0).replace("&", _FD_DUP_PLACEHOLDER), command)


def _unmask_fd_dup(segment):
    return segment.replace(_FD_DUP_PLACEHOLDER, "&")


def _is_segment_readonly(segment):
    # Command substitution runs its inner command regardless of the
    # outer command's own read-only status.
    if has_unsafe_substitution(segment):
        return False
    # A redirect makes any segment a write, whatever the command name —
    # this is what keeps heredoc file writes ("cat > f <<EOF") from
    # passing as read-only on the strength of "cat" alone — except a
    # target of /dev/null, which writes nothing.
    if any(target != _NULL_SINK for target in _REDIRECT_RE.findall(segment)):
        return False
    tokens = segment.split()
    if not tokens:
        return True
    first = tokens[0]
    second = tokens[1] if len(tokens) > 1 else ""
    if first == "find":
        return not any(t in _FIND_MUTATING_FLAGS for t in tokens[1:])
    if first == "yq":
        return not any(t in _YQ_MUTATING_FLAGS for t in tokens[1:])
    if first in READONLY_BARE_COMMANDS:
        return True
    if first == "sed":
        return "-n" in tokens[1:]
    if first == "command":
        return second == "-v"
    if first == "git":
        if second == "branch":
            return _is_git_branch_readonly(tokens[2:])
        return second in _GIT_READONLY_SUBCOMMANDS
    if first == "gh":
        third = tokens[2] if len(tokens) > 2 else ""
        if second == "pr" and third in {"view", "checks"}:
            return True
        if second == "issue" and third == "view":
            return True
        return False
    return False


def is_readonly_bash_command(command):
    """Return True if every segment of a Bash command is recognizably read-only.

    Segments are split on shell operators (&&, ||, ;, |, &, newline) via
    hook_utils.split_outside_quotes, so a chained command like
    ``git status && rm -rf x`` is judged on every segment, not only the
    first one. Unrecognized commands are treated as mutating — this is
    an allowlist, not a blocklist, so the default for anything not
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

    Chained with &&, ||, or ; — not just piped — every segment of the
    chain is checked, not only the first:

    >>> is_readonly_bash_command("git status && rm -rf /tmp/x")
    False
    >>> is_readonly_bash_command("git status; git log")
    True
    >>> is_readonly_bash_command("false || rm -rf /tmp/x")
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

    Bare-name allowlist entries that mutate under specific arguments are
    gated instead of being treated as unconditionally read-only:

    >>> is_readonly_bash_command("git branch")
    True
    >>> is_readonly_bash_command("git branch -a")
    True
    >>> is_readonly_bash_command("git branch -D feature")
    False
    >>> is_readonly_bash_command("git branch new-branch")
    False
    >>> is_readonly_bash_command("find . -name '*.py'")
    True
    >>> is_readonly_bash_command("find . -delete")
    False
    >>> is_readonly_bash_command("find . -exec rm {} +")
    False
    >>> is_readonly_bash_command("yq '.a' f.yaml")
    True
    >>> is_readonly_bash_command("yq -i '.a=1' f.yaml")
    False

    Command substitution runs its inner command regardless of the
    outer command's own status, forcing mutating even under an
    allowlisted outer command:

    >>> is_readonly_bash_command("ls $(rm -rf x)")
    False
    >>> is_readonly_bash_command("echo `rm -rf x`")
    False
    >>> is_readonly_bash_command("echo 'literal $(rm -rf x)'")
    True

    Unrecognized commands default to mutating:

    >>> is_readonly_bash_command("some-unknown-tool --flag")
    False

    A redirect makes the segment a write even when the command name is
    on the allowlist, which covers the heredoc file-write idiom — the
    one exception is a target of /dev/null, which writes nothing:

    >>> is_readonly_bash_command("cat > out.txt <<EOF")
    False
    >>> is_readonly_bash_command("echo hi >> log.txt")
    False
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
    masked = _mask_fd_dup(command)
    return all(
        _is_segment_readonly(_unmask_fd_dup(seg)) for seg in split_outside_quotes(masked)
    )


def extract_tool_calls(blocks):
    """Extract (name, command) tuples from tool_use blocks.

    command is populated only for Bash tool calls; every other tool
    gets None since the prefilter only needs the command text for Bash.
    An explicit null ``input`` (rather than a missing key) is checked
    for explicitly, since a ``.get`` default only fires on a missing
    key, not on a key present with a null value.

    >>> extract_tool_calls([
    ...     {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
    ... ])
    [('Bash', 'ls')]
    >>> extract_tool_calls([{"type": "tool_use", "name": "Edit", "input": {"file_path": "x"}}])
    [('Edit', None)]
    >>> extract_tool_calls([{"type": "tool_use", "name": "Bash", "input": None}])
    [('Bash', None)]
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
            tool_input = block.get("input")
            command = tool_input.get("command") if isinstance(tool_input, dict) else None
        calls.append((name, command))
    return calls


def is_mutating_turn(tool_calls):
    """Return True if a tool call in tool_calls shows the turn already did work.

    When this is True the hook skips the Haiku call entirely: ordinary
    working turns edit something, so they never pay for the network
    round trip. Only Edit/Write/NotebookEdit and a non-read-only Bash
    command count as mutating here — an Agent/Task dispatch to a
    subagent, or an MCP tool that writes on the far side of its own
    server, is not in MUTATING_TOOL_NAMES and is not modeled at all, so
    a turn that only delegates and then stops still reaches the Haiku
    call. That gap is the first place to look if this call is firing
    unexpectedly for a turn that clearly did do work.

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
    off the wire. Neither a thinking nor an output_config.effort field
    is sent, because Haiku 4.5 accepts neither: it is an
    extended-thinking-only model, where thinking type "adaptive"
    returns a 400, and Opus 4.5 is the only extended-thinking-only
    model that supports effort. See
    https://platform.claude.com/docs/en/build-with-claude/extended-thinking
    ("Migrating to adaptive thinking" and "Budget rules and tuning").

    >>> req = build_verdict_request(["I'll fix that next."], ["Read"])
    >>> req["model"]
    'claude-haiku-4-5'
    >>> req["max_tokens"]
    256
    >>> req["system"] == VERDICT_SYSTEM_PROMPT
    True
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
    >>> extract_verdict_text({"content": [
    ...     {"type": "text", "text": "first"},
    ...     {"type": "text", "text": "second"},
    ... ]})
    'first'
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
    hook. An off-contract reply (anything other than a clean YES or
    NO, case-insensitively) gets a stderr breadcrumb, so an operator
    can tell "Haiku said NO" apart from "Haiku replied off-contract and
    we dropped it".

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
        print("block_unkept_promise: verdict reply empty, treating as NO", file=sys.stderr)
        return False
    first_line = text.strip().splitlines()[0].strip()
    verdict = first_line.upper()
    if verdict not in ("YES", "NO"):
        print(
            f"block_unkept_promise: verdict reply off-contract, treating as NO: {first_line!r}",
            file=sys.stderr,
        )
    return verdict == "YES"


def call_haiku_verdict(texts, tool_names, api_key):
    """Call the Anthropic Messages API and return the boolean verdict.

    Any failure — network, timeout, malformed JSON, missing field, or
    an unparseable verdict — is swallowed and treated as NO with a
    stderr breadcrumb. The broad except below is deliberate: a Stop
    hook must never wedge a turn on a broken API call, whatever shape
    the failure takes.
    """
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
    except Exception as e:  # broad on purpose — see docstring
        print(f"block_unkept_promise: verdict call failed: {e!r}", file=sys.stderr)
        return False

    verdict_text = extract_verdict_text(response_json)
    if verdict_text is None:
        print("block_unkept_promise: verdict response missing text", file=sys.stderr)
        return False
    return parse_verdict(verdict_text)


def latest_assistant_uuid(events):
    """Return the uuid of the most recent assistant event, or None.

    A missing uuid on the assistant event itself silently disables the
    guard downstream (already_fired treats a None uuid as "skip the
    guard"), so it is worth its own example here:

    >>> latest_assistant_uuid([
    ...     {"type": "assistant", "uuid": "a1", "message": {"content": []}},
    ...     {"type": "user", "uuid": "u1", "message": {"content": "hi"}},
    ... ])
    'a1'
    >>> latest_assistant_uuid([{"type": "assistant", "message": {"content": []}}]) is None
    True
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
    """Build the guard's state-file path for a session, sanitizing hostile input.

    >>> _state_file_path("abc-123_XYZ") == os.path.join(
    ...     tempfile.gettempdir(), "block_unkept_promise_abc-123_XYZ.json"
    ... )
    True
    >>> _state_file_path("../../etc/passwd") == os.path.join(
    ...     tempfile.gettempdir(), "block_unkept_promise_______etc_passwd.json"
    ... )
    True
    >>> _state_file_path("") == os.path.join(
    ...     tempfile.gettempdir(), "block_unkept_promise_unknown.json"
    ... )
    True
    """
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", session_id) or "unknown"
    return os.path.join(tempfile.gettempdir(), f"block_unkept_promise_{safe_id}.json")


def _read_guard_state(session_id):
    """Read the guard state file.

    A missing file is the normal first-run case and returns {}
    silently. Any other read failure (corrupt JSON, permission denied,
    a truncated write from a killed process) is swallowed with a
    stderr breadcrumb and also treated as {} — a corrupt state file
    must degrade to letting the guard run again, not to disabling it
    forever.
    """
    path = _state_file_path(session_id)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except (OSError, ValueError) as e:
        print(f"block_unkept_promise: guard state read failed: {e!r}", file=sys.stderr)
        return {}


def already_fired(session_id, uuid):
    """Return True if the guard says this hook must not fire again.

    Two independent bounds live in the same state file:
    - the uuid bound: at most one firing per assistant message uuid.
    - the fire-count bound: at most MAX_FIRINGS_PER_SESSION firings per
      session. This is the bound that actually stops an asyncRewake
      loop — each wake produces a new assistant message with a new
      uuid, so the uuid bound alone never sees a repeat there.

    A missing session_id or uuid bypasses both bounds entirely, which
    is exactly the kind of silent disarm this guard exists to prevent,
    so it is logged rather than passed through quietly.
    """
    if not session_id or not uuid:
        print(
            f"block_unkept_promise: guard bypassed, missing session_id={session_id!r} "
            f"or uuid={uuid!r}",
            file=sys.stderr,
        )
        return False
    state = _read_guard_state(session_id)
    if state.get("last_fired_uuid") == uuid:
        return True
    if state.get("fire_count", 0) >= MAX_FIRINGS_PER_SESSION:
        return True
    return False


def record_fired(session_id, uuid):
    """Persist the uuid this hook just fired on and bump the fire count.

    Written atomically (temp file in the same directory, then
    os.replace) so a process killed mid-write never leaves a truncated
    state file for _read_guard_state() to stumble over — os.replace is
    a single filesystem rename, not a byte-by-byte write, so there is
    no window where the destination path holds a partial file.
    """
    if not session_id or not uuid:
        print(
            f"block_unkept_promise: record_fired called with missing "
            f"session_id={session_id!r} or uuid={uuid!r}",
            file=sys.stderr,
        )
        return
    state = _read_guard_state(session_id)
    state["last_fired_uuid"] = uuid
    state["fire_count"] = state.get("fire_count", 0) + 1
    path = _state_file_path(session_id)
    tmp_path = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(state, f)
        os.replace(tmp_path, path)
    except OSError as e:
        print(f"block_unkept_promise: record_fired write failed: {e!r}", file=sys.stderr)
        try:
            os.remove(tmp_path)
        except OSError:
            pass


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
