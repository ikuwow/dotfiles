#!/usr/bin/env python3
"""Stop hook: pause once when the assistant emits excuse-preamble phrases.

AIRULES.md (the 「正直」「本当のところ」「ぶっちゃけ」 ban under
応答の姿勢と判断) forbids these as 断り書き (preamble that softens
or qualifies an opinion).
The model knows the rule but slips. A literal substring match cannot
disambiguate legitimate uses (名詞 like 「正直者」), so this hook does
not try. It does exclude one legitimate case: text inside backtick
code spans (inline `...` or fenced ``` blocks) is a *mention*, not a
*use*, of the phrase (e.g. quoting it in a retrospective Problem
line), so it is stripped before matching. Other legitimate uses
remain accepted false positives, pinned below. It blocks at most once
per Stop chain: the second invocation arrives with
stop_hook_active=true and is allowed through, preventing infinite
loops.

I/O failures (stdin parse, missing transcript_path, transcript read,
poll timeout) are swallowed and the hook exits 0 — a Stop hook that
wedges the assistant is far worse than one that silently no-ops. A
short stderr message is emitted on each terminal fall-through so the
operator can grep hook logs to distinguish "rule not violated" from
"hook silently broken". Transient read failures inside the poll loop
are retried silently; the last one is surfaced via the timeout
breadcrumb if the loop exhausts.

For pure-text turns (no tool calls), Claude Code can invoke the Stop
hook before the assistant event is flushed to the transcript JSONL.
When the initial read returns no current-turn assistant text, the
hook polls the transcript at POLL_INTERVAL_S intervals up to
POLL_MAX_ITERATIONS iterations before giving up fail-open. See PR
#153 for the empirical basis of these values.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import re
import sys
import time

FORBIDDEN_PATTERN = re.compile(r"正直|本当のところ|ぶっちゃけ")

POLL_INTERVAL_S = 0.05
POLL_MAX_ITERATIONS = 10

REASON = (
    "Your response contains one of 「正直」「本当のところ」「ぶっちゃけ」.\n\n"
    "The string match alone cannot tell whether you used it as 断り書き "
    "(preamble softening or qualifying an opinion, banned by AIRULES.md) "
    "or in a sense the rule does not target. Reconsider.\n\n"
    "Why 断り書き usage is harmful: prefacing a statement with 「正直」 "
    "plants the doubt that everything else you have said was not honest. "
    "The damage is retroactive (it taints prior statements) and "
    "prospective (it taints future ones), and it cannot be unplanted. "
    "「本当のところ」「ぶっちゃけ」 carry the same structural harm.\n\n"
    "Judge your own usage and rewrite if it was 断り書き.\n\n"
    "When you need to mention (not use) a banned phrase — e.g. quoting "
    "it in a retrospective Problem line — wrap it in backticks so this "
    "hook can tell mention from use."
)


def is_forbidden(text):
    """Return True if text contains a 断り書き phrase listed in AIRULES.md.

    Hits as 断り書き (the target use):

    >>> is_forbidden("正直それは下がると思う")
    True
    >>> is_forbidden("本当のところ判断が難しい")
    True
    >>> is_forbidden("ぶっちゃけ無理やと思う")
    True

    The regex deliberately matches legitimate uses too — these
    intentional false positives are pinned so a future tightening of
    the regex breaks the test:

    >>> is_forbidden("彼は正直者だ")
    True

    Negatives:

    >>> is_forbidden("commit を push しといた")
    False
    >>> is_forbidden("")
    False
    """
    return bool(FORBIDDEN_PATTERN.search(text))


_FENCE_RE = re.compile(r"^(```|~~~)")
_INLINE_CODE_RE = re.compile(r"`[^`]*`")


def _strip_inline_code(line):
    """Remove paired inline backtick spans from a single line.

    A trailing unpaired backtick truncates the rest of the line —
    there is no closing backtick to pair with, so everything after it
    is inside an unterminated span and is dropped rather than risking
    a false match on the fragment that follows.
    """
    line = _INLINE_CODE_RE.sub("", line)
    if line.count("`") % 2 == 1:
        line = line[: line.rfind("`")]
    return line


def strip_code_spans(text):
    """Remove fenced code blocks and inline backtick spans from text.

    Code spans are a *mention*, not a *use*, of a phrase — quoting a
    banned phrase in backticks to talk about it (e.g. a retrospective
    Problem line) should not trip the hook the way actually using it
    as 断り書き would.

    Banned phrase inside an inline backtick span is removed, the rest
    of the line is kept:

    >>> strip_code_spans("説明: `正直`は禁止らしい")
    '説明: は禁止らしい'

    Banned phrase inside a fenced code block is removed, fences
    included:

    >>> strip_code_spans("before\\n```\\n正直\\n```\\nafter")
    'before\\nafter'

    Banned phrase outside any code span is preserved:

    >>> strip_code_spans("正直それは無理やと思う")
    '正直それは無理やと思う'

    An unpaired trailing fence is treated as an unterminated code
    block: everything from the fence onward is dropped rather than
    risking a false negative on unterminated content:

    >>> strip_code_spans("before\\n```\\n正直")
    'before'

    An unpaired trailing backtick truncates the line at the backtick:

    >>> strip_code_spans("正直 before ` after")
    '正直 before '
    """
    out_lines = []
    in_fence = False
    for line in text.split("\n"):
        if _FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        out_lines.append(_strip_inline_code(line))
    return "\n".join(out_lines)


def collect_current_turn_assistant_text(events):
    """Collect assistant text blocks emitted since the last real user message.

    Walks events backward. Stops at a real user message. user events
    whose content is purely tool_result blocks are tool-call re-entries
    and are skipped, not treated as turn boundaries.

    Returns a list of per-block strings (reverse-walk order) rather
    than one joined string, so strip_code_spans can be applied per
    block: joining first would let an unpaired fence in one block
    silently swallow the prose — and any banned phrase — of every
    other block.

    Single-turn capture:

    >>> events = [
    ...     {"type": "user", "message": {"role": "user", "content": "hi"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "正直そう思う"}
    ...     ]}},
    ... ]
    >>> collect_current_turn_assistant_text(events)
    ['正直そう思う']

    Tool-call re-entry does not end the turn; both text blocks are
    captured (in reverse-walk order):

    >>> events = [
    ...     {"type": "user", "message": {"role": "user", "content": "x"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "first"}
    ...     ]}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "tool_use", "name": "Bash"}
    ...     ]}},
    ...     {"type": "user", "message": {"role": "user", "content": [
    ...         {"type": "tool_result", "content": "ok"}
    ...     ]}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "second"}
    ...     ]}},
    ... ]
    >>> collect_current_turn_assistant_text(events)
    ['second', 'first']

    A real user message ends the scan; older turns are not captured:

    >>> events = [
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "old"}
    ...     ]}},
    ...     {"type": "user", "message": {"role": "user", "content": "new turn"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "current"}
    ...     ]}},
    ... ]
    >>> collect_current_turn_assistant_text(events)
    ['current']

    Empty input:

    >>> collect_current_turn_assistant_text([])
    []

    Malformed events are skipped silently — system events, assistant
    messages with missing or null content, etc. — so the hook does not
    crash on unfamiliar transcript shapes. Real transcript events also
    carry uuid / timestamp / parentUuid / sessionId fields not shown
    here; only the keys read above matter.

    >>> events = [
    ...     {"type": "system"},
    ...     {"type": "assistant", "message": {}},
    ...     {"type": "assistant", "message": {"content": None}},
    ...     {"type": "user", "message": {"role": "user", "content": "hi"}},
    ...     {"type": "assistant", "message": {"content": [
    ...         {"type": "text", "text": "正直そう思う"}
    ...     ]}},
    ... ]
    >>> collect_current_turn_assistant_text(events)
    ['正直そう思う']
    """
    texts = []
    for event in reversed(events):
        if event.get("type") == "user":
            content = event.get("message", {}).get("content")
            if isinstance(content, str):
                break
            if isinstance(content, list) and not all(
                isinstance(c, dict) and c.get("type") == "tool_result"
                for c in content
            ):
                break
            continue
        if event.get("type") != "assistant":
            continue
        for block in event.get("message", {}).get("content", []) or []:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
    return texts


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_excuse_phrases: stdin parse failed: {e}", file=sys.stderr)
        sys.exit(0)

    if data.get("stop_hook_active"):
        sys.exit(0)

    transcript_path = data.get("transcript_path", "")
    if not transcript_path:
        print("block_excuse_phrases: no transcript_path in stdin", file=sys.stderr)
        sys.exit(0)

    try:
        with open(transcript_path, encoding="utf-8") as f:
            events = [json.loads(line) for line in f if line.strip()]
    except (OSError, json.JSONDecodeError) as e:
        print(f"block_excuse_phrases: transcript read failed: {e}", file=sys.stderr)
        sys.exit(0)

    blocks = collect_current_turn_assistant_text(events)

    if not blocks:
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
            blocks = collect_current_turn_assistant_text(events)
            if blocks:
                break

        if not blocks:
            elapsed_ms = int((time.monotonic() - poll_start) * 1000)
            err_suffix = f" last_err={last_err!r}" if last_err else ""
            print(
                f"block_excuse_phrases: poll timeout after {elapsed_ms}ms "
                f"events={len(events)} transcript={transcript_path}{err_suffix}",
                file=sys.stderr,
            )
            sys.exit(0)

    if any(is_forbidden(strip_code_spans(block)) for block in blocks):
        print(json.dumps({"decision": "block", "reason": REASON}))
    sys.exit(0)


if __name__ == "__main__":
    main()
