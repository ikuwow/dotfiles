"""Score every reply, repeatedly and with a second model. Writes judgements.jsonl.

An earlier run, before this harness existed, scored each reply once and treated
the result as fact. Here each reply is judged config.JUDGE_PASSES times by the
primary judge and once by a different model, so that disagreement is visible in
the output instead of hidden inside a single call.

Hand-written controls with known labels are judged in the same pass, including
borderline cases, so the judge's discrimination is measured on this run rather
than assumed from a previous one.

`--controls-only` judges nothing but those hand-written texts. The energy axis
decides which wording ships in round 2, so the rubric should be shown to
separate bright delivery from a loud report and from warm-but-flat prose before
any replies are generated -- the controls are a handful of calls where the
generation is tens of dollars. Nothing enforces that order; it is the procedure
in README.md, and `run.py` will generate replies whether the gate ran or not.
"""

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import config

REPLIES_FILE = os.path.join(config.DATA_DIR, "replies.jsonl")
CONTROLS_FILE = "controls.jsonl"
JUDGEMENTS_FILE = os.path.join(config.DATA_DIR, "judgements.jsonl")
CONTROL_JUDGEMENTS_FILE = os.path.join(config.DATA_DIR, "judgements-controls.jsonl")
MAX_WORKERS = 8
RUBRIC_KEYS = ("register", "tameguchi", "energy_level", "empathy_padding")

def claude(model, prompt):
    result = subprocess.run(
        ["claude", "-p", "--safe-mode", "--tools", "", "--model", model,
         "--output-format", "json", "--system-prompt", config.JUDGE_RUBRIC, prompt],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr[:300] or result.stdout[:300])
    return json.loads(result.stdout).get("result", "")


def parse(raw):
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def judge_one(record, model, pass_index):
    row = {
        "cell": record["cell"],
        "rep": record["rep"],
        "turn": record["turn"],
        "style": record.get("style"),
        "expected": record.get("expected"),
        "expected_energy_high": record.get("expected_energy_high"),
        "expected_empathy": record.get("expected_empathy"),
        "judge_model": model,
        "pass": pass_index,
    }
    try:
        # Only the rubric's own keys are taken. `update()` with the raw object
        # would let the judge overwrite the identity fields and, worse, the
        # `expected_*` labels it is being graded against -- a reply echoing
        # `"expected"` back would grade itself and the control gate would print
        # a perfect score having checked nothing. A missing key raises here
        # rather than reaching analyze.py as a silent False vote.
        parsed = parse(claude(model, "判定対象:\n\n" + record["text"]))
        row.update({k: parsed[k] for k in RUBRIC_KEYS})
    except Exception as exc:  # noqa: BLE001 - record the failure, keep going
        row["error"] = str(exc)[:300]
    return row


def main():
    controls_only = "--controls-only" in sys.argv
    output_file = CONTROL_JUDGEMENTS_FILE if controls_only else JUDGEMENTS_FILE
    sources = (CONTROLS_FILE,) if controls_only else (REPLIES_FILE, CONTROLS_FILE)

    # Keyed rather than appended: a restarted run can leave a second copy of a
    # conversation in replies.jsonl, and judging both would put two different
    # texts under one identifier in the analysis. Last one wins.
    by_key = {}
    for path in sources:
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    if "error" not in record:
                        by_key[(record["cell"], record["rep"], record["turn"])] = record
        except FileNotFoundError:
            hint = "run run.py first" if path == REPLIES_FILE else "it is committed"
            sys.exit(f"{path} not found; {hint}")
    records = list(by_key.values())

    jobs = []
    for record in records:
        for index in range(1, config.JUDGE_PASSES + 1):
            jobs.append((record, config.JUDGE_MODEL, index))
        jobs.append((record, config.CROSS_JUDGE_MODEL, 1))

    print(f"{len(jobs)} judgements over {len(records)} texts", flush=True)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        rows = list(pool.map(lambda job: judge_one(*job), jobs))

    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    errors = sum(1 for row in rows if "error" in row)
    print(f"wrote {output_file}: {len(rows)} rows, {errors} errors")


if __name__ == "__main__":
    main()
