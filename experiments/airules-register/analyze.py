"""Aggregate judgements.jsonl and replies.jsonl into the reported figures.

Reports, in order: whether the judge is trustworthy on this run, then the
register results it is being trusted for, then the descriptive axes.
"""

import json
import re
from collections import Counter, defaultdict

import config

REPLIES_FILE = "replies.jsonl"
JUDGEMENTS_FILE = "judgements.jsonl"

# Surface markers for the energy axis. The instruction it stands for is
# under-specified, so this is reported alongside the judge's call rather than
# used to decide anything.
ENERGY_MARKERS = re.compile(r"[!！]|^(?:お|あ|わ|へえ|ほんま|なるほど|やば)", re.MULTILINE)


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def key(row):
    return (row["cell"], row["rep"], row["turn"])


def main():
    replies = {key(r): r for r in load(REPLIES_FILE) if "error" not in r}
    judgements = [j for j in load(JUDGEMENTS_FILE) if "error" not in j]

    primary = defaultdict(list)
    cross = {}
    for row in judgements:
        if row["judge_model"] == config.JUDGE_MODEL:
            primary[key(row)].append(row)
        else:
            cross[key(row)] = row

    # 1. Judge reliability, before any result that depends on it.
    unanimous = 0
    measured = 0
    for identifier, rows in primary.items():
        if len(rows) < config.JUDGE_PASSES:
            continue
        measured += 1
        if len({r["register"] for r in rows}) == 1:
            unanimous += 1
    print("judge reliability")
    print(f"  repeat agreement on register: {unanimous}/{measured} texts unanimous "
          f"across {config.JUDGE_PASSES} passes")

    cross_agree = sum(
        1
        for identifier, rows in primary.items()
        if identifier in cross
        and Counter(r["register"] for r in rows).most_common(1)[0][0]
        == cross[identifier]["register"]
    )
    print(f"  agreement with {config.CROSS_JUDGE_MODEL}: {cross_agree}/{len(cross)}")

    controls = [
        (identifier, rows)
        for identifier, rows in primary.items()
        if identifier[0].startswith("control-")
    ]
    correct = 0
    for identifier, rows in controls:
        expected = rows[0].get("expected")
        majority = Counter(r["register"] for r in rows).most_common(1)[0][0]
        mark = "ok" if majority == expected else "MISS"
        if majority == expected:
            correct += 1
        print(f"  {identifier[0]:<28} expected={expected:<9} got={majority:<9} {mark}")
    print(f"  controls correct: {correct}/{len(controls)}")

    # 2. Register by cell, using the majority judgement.
    by_cell = defaultdict(list)
    by_cell_style = defaultdict(list)
    by_cell_turn = defaultdict(dict)
    for identifier, rows in primary.items():
        if identifier[0].startswith("control-"):
            continue
        cell, rep, turn = identifier
        majority = Counter(r["register"] for r in rows).most_common(1)[0][0]
        tameguchi = sum(1 for r in rows if r.get("tameguchi")) > len(rows) / 2
        energy = sum(1 for r in rows if r.get("high_energy")) > len(rows) / 2
        style = replies[identifier].get("style")
        entry = {"register": majority, "tameguchi": tameguchi, "energy": energy}
        by_cell[cell].append(entry)
        by_cell_style[(cell, style)].append(entry)
        by_cell_turn[cell][(rep, turn)] = majority

    print()
    print("register by cell")
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        n = len(rows)
        kansai = sum(1 for r in rows if r["register"] == "kansai")
        tame = sum(1 for r in rows if r["tameguchi"])
        breakdown = " ".join(
            f"{k}={v}" for k, v in sorted(Counter(r["register"] for r in rows).items())
        )
        print(f"  {cell:<20} kansai {kansai:>3}/{n:<3} tameguchi {tame:>3}/{n:<3}  {breakdown}")

    # 3. Mirroring: does the user's own register change the result?
    print()
    print("register by the style of the user's turn")
    styles = ["plain", "desumasu", "casual"]
    print(f"  {'cell':<20} " + " ".join(f"{s:>10}" for s in styles))
    for cell in sorted(by_cell):
        parts = []
        for style in styles:
            rows = by_cell_style.get((cell, style), [])
            if not rows:
                parts.append(f"{'-':>10}")
                continue
            kansai = sum(1 for r in rows if r["register"] == "kansai")
            parts.append(f"{kansai:>6}/{len(rows):<3}")
        print((f"  {cell:<20} " + " ".join(parts)).rstrip())

    # 4. Decay: register per turn index, averaged over repetitions.
    print()
    print("kansai rate by turn index")
    turns = sorted({t for cell in by_cell_turn.values() for _, t in cell})
    print((f"  {'cell':<20} " + " ".join(f"t{t:<3}" for t in turns)).rstrip())
    for cell in sorted(by_cell_turn):
        parts = []
        for turn in turns:
            values = [v for (_, t), v in by_cell_turn[cell].items() if t == turn]
            hits = sum(1 for v in values if v == "kansai")
            parts.append(f"{hits}/{len(values)}" if values else "-")
        print((f"  {cell:<20} " + " ".join(f"{p:<4}" for p in parts)).rstrip())

    # 5. First person: violations, not occurrences.
    print()
    print("first person (occurrences of the specified set vs anything else)")
    for cell in sorted({c for c, _, _ in replies if not c.startswith("control-")}):
        texts = [r["text"] for k, r in replies.items() if k[0] == cell]
        joined = "\n".join(texts)
        specified = {p: joined.count(p) for p in config.SPECIFIED_PRONOUNS}
        other = {p: joined.count(p) for p in config.OTHER_PRONOUNS if joined.count(p)}
        total = sum(specified.values())
        print(f"  {cell:<20} specified={total:<4} " +
              (f"other={other}" if other else "other=none"))

    # 6. Energy, descriptive only.
    print()
    print("energy (judge call, and surface markers per reply — descriptive only)")
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        judged = sum(1 for r in rows if r["energy"])
        texts = [r["text"] for k, r in replies.items() if k[0] == cell]
        markers = sum(len(ENERGY_MARKERS.findall(t)) for t in texts) / max(len(texts), 1)
        print(f"  {cell:<20} judge {judged:>3}/{len(rows):<3}  markers/reply {markers:.1f}")

    cost = sum(r.get("cost_usd") or 0 for r in replies.values())
    print()
    print(f"generation cost reported at list price: ${cost:.2f}")


if __name__ == "__main__":
    main()
