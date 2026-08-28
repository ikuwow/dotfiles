#!/usr/bin/env python3
"""Stop hook: catch turns that promise work and then end without doing it.

Asks a Claude Haiku model whether the current turn committed to work
and then ended without starting it, given the turn's final assistant
text. Reads that text from last_assistant_message on the Stop event's
stdin payload — the field the hooks reference documents for exactly
this ("last_assistant_message on Stop and SubagentStop"). Silent no-op
unless CLAUDE_STOP_CHECK_ANTHROPIC_API_KEY is set.

On a YES verdict the hook writes to stderr and exits 2 — a contract
that works for both a synchronous Stop hook and one registered with
asyncRewake: true. Whether asyncRewake actually fires on a live Stop
event is unverified; if it does not, deleting that one settings.json
flag needs no code change. stop_hook_active is the only loop guard.

Every failure (stdin parse, the API call) is swallowed with a stderr
breadcrumb and the hook exits 0 rather than wedging the turn.

Spec: https://code.claude.com/docs/en/hooks
"""
import json
import os
import sys
import urllib.error
import urllib.request

API_KEY_ENV = "CLAUDE_STOP_CHECK_ANTHROPIC_API_KEY"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 256
TIMEOUT_S = 8

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
    "That judgment came from a Haiku classifier reading this turn's final "
    "text, not a keyword match — it can be wrong, including on turns that "
    "are legitimately waiting on you or the user, or that already stated a "
    "reason to defer.\n\n"
    "Judge your own turn: if you committed to doing something, do it now. "
    "If you are deliberately not doing it in this turn, say so explicitly."
)


def build_verdict_request(text):
    """Build the Messages API request body.

    Omits thinking/output_config.effort: Haiku 4.5 is extended-
    thinking-only (adaptive thinking type 400s on it) and Opus 4.5 is
    the only extended-thinking-only model that supports effort. See
    https://platform.claude.com/docs/en/build-with-claude/extended-thinking
    ("Migrating to adaptive thinking" and "Budget rules and tuning").
    """
    return {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": VERDICT_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": f"Assistant turn text:\n{text}"}],
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


def call_haiku_verdict(text, api_key):
    """Call the Messages API and return the boolean verdict; any failure is NO."""
    request_body = build_verdict_request(text)
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


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"block_unkept_promise: stdin parse failed: {e!r}", file=sys.stderr)
        sys.exit(0)

    if data.get("stop_hook_active"):
        sys.exit(0)

    api_key = os.environ.get(API_KEY_ENV, "")
    if not api_key:
        sys.exit(0)

    text = data.get("last_assistant_message")
    if not text:
        print("block_unkept_promise: no last_assistant_message in stdin", file=sys.stderr)
        sys.exit(0)

    if call_haiku_verdict(text, api_key):
        print(REASON, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
