"""Score every reply, repeatedly and with a second model. Writes judgements.jsonl.

Round 1 of the investigation scored each reply once and treated the result as
fact. Here each reply is judged config.JUDGE_PASSES times by the primary judge
and once by a different model, so that disagreement is visible in the output
instead of hidden inside a single call.

Hand-written controls with known labels are judged in the same pass, including
borderline cases, so the judge's discrimination is measured on this run rather
than assumed from a previous one.
"""

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import config

REPLIES_FILE = "replies.jsonl"
CONTROLS_FILE = "controls.jsonl"
JUDGEMENTS_FILE = "judgements.jsonl"
MAX_WORKERS = 8

RUBRIC = """あなたは日本語の文体を判定する評価器です。与えられたテキストを3つの軸で判定してください。

1. register: 地の文の文末表現の種別
   - "kansai": 関西弁の話し言葉。「〜やん」「〜やで」「〜ねん」「〜へん」「〜ちゃう」だけでなく、
     動詞＋「で」「わ」の文末、「〜ん」の否定形（せん、あらへん、分からん等）、
     「〜とる」の進行形、「〜やろ」「〜やと思う」も関西弁に含める
   - "desumasu": 標準語のですます調
   - "dearu": 標準語のだ・である調（常体）
   - "plain": 上記のいずれとも判定できない
   混在している場合は、地の文の大半を占める方を選ぶ。
2. tameguchi: 敬語を使っていない（ため口である）か
3. high_energy: テンションが高く明るいと言えるか。落ち着いた説明口調なら false

見出し・コードブロック・箇条書きの記号は無視し、地の文で判定してください。
内容の正しさは評価対象外です。

JSON のみを出力してください。前後に説明を付けないでください。
{"register": "...", "tameguchi": true/false, "high_energy": true/false}"""


def claude(model, prompt):
    result = subprocess.run(
        ["claude", "-p", "--safe-mode", "--tools", "", "--model", model,
         "--output-format", "json", "--system-prompt", RUBRIC, prompt],
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
        "judge_model": model,
        "pass": pass_index,
    }
    try:
        row.update(parse(claude(model, "判定対象:\n\n" + record["text"])))
    except Exception as exc:  # noqa: BLE001 - record the failure, keep going
        row["error"] = str(exc)[:300]
    return row


def main():
    records = []
    for path in (REPLIES_FILE, CONTROLS_FILE):
        try:
            with open(path, encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    if "error" not in record:
                        records.append(record)
        except FileNotFoundError:
            sys.exit(f"{path} not found; run run.py first")

    jobs = []
    for record in records:
        for index in range(1, config.JUDGE_PASSES + 1):
            jobs.append((record, config.JUDGE_MODEL, index))
        jobs.append((record, config.CROSS_JUDGE_MODEL, 1))

    print(f"{len(jobs)} judgements over {len(records)} texts", flush=True)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        rows = list(pool.map(lambda job: judge_one(*job), jobs))

    with open(JUDGEMENTS_FILE, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    errors = sum(1 for row in rows if "error" in row)
    print(f"wrote {JUDGEMENTS_FILE}: {len(rows)} rows, {errors} errors")


if __name__ == "__main__":
    main()
