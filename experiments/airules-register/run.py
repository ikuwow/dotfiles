"""Generate the replies. Appends to replies.jsonl.

Each cell is a wording from config.wordings(); each conversation is one
`claude` process fed every turn of config.PROBE_TURNS over stream-json input.

The whole conversation has to run inside one process. `--resume` starts a new
process, and a resumed session does not carry the `--system-prompt-file` given
on the first turn — verified with a system prompt demanding a fixed token in
every reply, which turn 1 obeyed and the resumed turn 2 did not. A run built on
--resume therefore measures a register instruction present only on the opening
turn, which is not the condition being investigated.

--safe-mode disables CLAUDE.md discovery, skills, hooks and MCP, and --tools ""
removes the tool definitions, so the request carries the supplied system prompt
and nothing else from the local Claude Code configuration.

Each conversation is appended as it completes, and conversations already
recorded are skipped, so a run interrupted by a rate limit or a killed process
can be restarted with the same command and will only redo what is missing.
"""

import json
import os
import subprocess
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import config

REPLIES_FILE = os.path.join(config.DATA_DIR, "replies.jsonl")
MAX_WORKERS = 5

_write_lock = threading.Lock()


def user_event(text):
    return json.dumps(
        {"type": "user",
         "message": {"role": "user", "content": [{"type": "text", "text": text}]}},
        ensure_ascii=False,
    ) + "\n"


def claude(system_path):
    """Drive one conversation, sending each turn only after the previous result.

    Writing every turn up front does not work: user messages that arrive while
    the model is generating are merged into the turn in progress, and ten
    messages come back as four replies.
    """
    process = subprocess.Popen(
        ["claude", "-p", "--safe-mode", "--tools", "", "--model", config.MODEL,
         "--system-prompt-file", system_path,
         "--input-format", "stream-json", "--output-format", "stream-json", "--verbose"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        # Discarded rather than piped: nothing reads it, and an unread pipe that
        # fills stops the child mid-turn with no error and no output. The result
        # event carries what a failure needs to say.
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    replies = []
    cost = 0.0
    try:
        for _, probe in config.PROBE_TURNS:
            process.stdin.write(user_event(probe))
            process.stdin.flush()

            reply = ""
            while True:
                line = process.stdout.readline()
                if not line:
                    raise RuntimeError("stream ended before the turn completed")
                if not line.strip():
                    continue
                event = json.loads(line)
                if event.get("type") == "assistant":
                    reply += "".join(
                        block.get("text", "")
                        for block in event["message"].get("content", [])
                        if block.get("type") == "text"
                    )
                elif event.get("type") == "result":
                    if event.get("is_error"):
                        raise RuntimeError(str(event.get("result"))[:400])
                    cost += event.get("total_cost_usd") or 0
                    break
            replies.append(reply)
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=120)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise

    return replies, cost


def append(records):
    with _write_lock:
        with open(REPLIES_FILE, "a", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")


def complete_conversations():
    """(cell, rep) pairs holding every turn index.

    Completeness is the set of turn indices, not a row count: two torn writes of
    six turns each sum to twelve and would pass a count test while turns 7-10
    were missing for good.

    A conversation that failed is retried, and its error row stays in the file.
    The retry appends a second set of rows; judge.py keys on (cell, rep, turn)
    and keeps the last, so the successful attempt is the one analysed -- and the
    stale error row must not keep the pair out of `done`, or every later run
    regenerates a conversation that already succeeded.
    """
    if not os.path.exists(REPLIES_FILE):
        return set()
    wanted = set(range(1, len(config.PROBE_TURNS) + 1))
    turns = defaultdict(set)
    with open(REPLIES_FILE, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if "error" not in record:
                turns[(record["cell"], record["rep"])].add(record["turn"])
    return {pair for pair, indices in turns.items() if indices >= wanted}


def run_conversation(cell, rep, system_path):
    try:
        replies, cost = claude(system_path)
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        append([{"cell": cell, "rep": rep, "error": str(exc)[:400]}])
        print(f"  {cell} rep{rep}: FAILED {str(exc)[:120]}", flush=True)
        return

    records = []
    for index, ((style, _), text) in enumerate(
            zip(config.PROBE_TURNS, replies, strict=True), start=1):
        records.append({"cell": cell, "rep": rep, "turn": index, "style": style,
                        "cost_usd": cost if index == 1 else None, "text": text})
    append(records)
    print(f"  {cell} rep{rep}: {len(records)} turns", flush=True)


def main():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(config.BASE_SYSTEM_FILE, encoding="utf-8") as f:
        base = f.read().strip()
    with open(config.AIRULES_FILE, encoding="utf-8") as f:
        airules = f.read().strip()

    done = complete_conversations()
    jobs = []
    for cell, block in config.wordings(airules):
        path = f"system-{cell}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(config.system_prompt(base, block))
        for rep in range(1, config.REPETITIONS + 1):
            if (cell, rep) not in done:
                jobs.append((cell, rep, path))

    skipped = len(config.wordings(airules)) * config.REPETITIONS - len(jobs)
    print(f"{len(jobs)} conversations x {len(config.PROBE_TURNS)} turns on "
          f"{config.MODEL} ({skipped} already recorded)", flush=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        list(pool.map(lambda job: run_conversation(*job), jobs))

    with open(REPLIES_FILE, encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    errors = sum(1 for r in records if "error" in r)
    cost = sum(r.get("cost_usd") or 0 for r in records)
    print(f"{REPLIES_FILE}: {len(records)} rows, {errors} errors, "
          f"${cost:.2f} reported at list price")


if __name__ == "__main__":
    main()
