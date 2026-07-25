"""Generate the replies. Appends to replies.jsonl.

Each cell is a wording from config.wordings(); each run is one conversation of
config.PROBE_TURNS turns, continued with --resume so the model sees a real
multi-turn history rather than a rebuilt prompt.

--safe-mode disables CLAUDE.md discovery, skills, hooks and MCP, and --tools ""
removes the tool definitions, so the request carries the supplied system prompt
and nothing else from the local Claude Code configuration.

Each turn is appended as it completes, and conversations already complete in
replies.jsonl are skipped, so a run interrupted by a rate limit or a killed
process can be restarted with the same command and will only redo what is
missing. A conversation that stopped part-way is redone from its first turn,
because the session it was continuing is not resumed across invocations.
"""

import json
import os
import subprocess
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import config

REPLIES_FILE = "replies.jsonl"
MAX_WORKERS = 5

_write_lock = threading.Lock()


def claude(args, prompt):
    result = subprocess.run(
        ["claude", "-p", "--safe-mode", "--tools", "", "--model", config.MODEL,
         "--output-format", "json", *args, prompt],
        capture_output=True,
        text=True,
        timeout=900,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[:400] or result.stdout[:400])
    body = json.loads(result.stdout)
    if body.get("is_error"):
        # Rate limits and quota exhaustion arrive this way, with exit code 0.
        raise RuntimeError(str(body.get("result"))[:400])
    return body


def append(record):
    with _write_lock:
        with open(REPLIES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def completed_conversations():
    """(cell, rep) pairs that already have every turn recorded without error."""
    if not os.path.exists(REPLIES_FILE):
        return set()
    turns = Counter()
    failed = set()
    with open(REPLIES_FILE, encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            pair = (record["cell"], record["rep"])
            if "error" in record:
                failed.add(pair)
            else:
                turns[pair] += 1
    return {
        pair
        for pair, count in turns.items()
        if count >= len(config.PROBE_TURNS) and pair not in failed
    }


def run_conversation(cell, rep, system_path):
    session = None
    for index, (style, probe) in enumerate(config.PROBE_TURNS, start=1):
        args = ["--system-prompt-file", system_path] if session is None else ["--resume", session]
        try:
            body = claude(args, probe)
        except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            append({"cell": cell, "rep": rep, "turn": index, "style": style,
                    "error": str(exc)[:400]})
            print(f"  {cell} rep{rep} turn{index}: FAILED {str(exc)[:120]}", flush=True)
            return
        session = body["session_id"]
        append(
            {
                "cell": cell,
                "rep": rep,
                "turn": index,
                "style": style,
                "cost_usd": body.get("total_cost_usd"),
                "text": body.get("result", ""),
            }
        )
        print(f"  {cell} rep{rep} turn{index} ({style}): "
              f"{len(body.get('result', ''))} chars", flush=True)


def main():
    with open(config.BASE_SYSTEM_FILE, encoding="utf-8") as f:
        base = f.read().strip()
    with open(config.AIRULES_FILE, encoding="utf-8") as f:
        airules = f.read().strip()

    jobs = []
    for cell, block in config.wordings(airules):
        path = f"system-{cell}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(config.system_prompt(base, block))
        for rep in range(1, config.REPETITIONS + 1):
            jobs.append((cell, rep, path))

    turns = len(config.PROBE_TURNS)
    print(f"{len(jobs)} conversations x {turns} turns on {config.MODEL}", flush=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = [pool.submit(run_conversation, *job) for job in jobs]
        records = [record for future in futures for record in future.result()]

    with open(REPLIES_FILE, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    errors = sum(1 for r in records if "error" in r)
    cost = sum(r.get("cost_usd") or 0 for r in records)
    print(f"wrote {REPLIES_FILE}: {len(records)} replies, {errors} errors, "
          f"${cost:.2f} reported at list price")


if __name__ == "__main__":
    main()
