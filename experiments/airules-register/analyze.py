"""Aggregate the recorded judgements into the reported figures.

Reports, in order: whether the judge is trustworthy on this run, then the
register results it is being trusted for, then energy and the empathy flag.

`--controls-only` reads `judgements-controls.jsonl` and stops after the
reliability section, which is the gate run before any replies are generated.
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict

import config

REPLIES_FILE = os.path.join(config.DATA_DIR, "replies.jsonl")
JUDGEMENTS_FILE = os.path.join(config.DATA_DIR, "judgements.jsonl")
CONTROL_JUDGEMENTS_FILE = os.path.join(config.DATA_DIR, "judgements-controls.jsonl")

ENERGY_MARKERS = re.compile(config.ENERGY_MARKER_PATTERN, re.MULTILINE)


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def key(row):
    return (row["cell"], row["rep"], row["turn"])


def is_high(row):
    """The judge's ordinal collapsed to the boolean the cells are compared on."""
    level = row.get("energy_level")
    return isinstance(level, int) and level >= config.ENERGY_HIGH_THRESHOLD


def majority(rows, predicate):
    return sum(1 for r in rows if predicate(r)) > len(rows) / 2


def report_reliability(primary, cross):
    """Everything that has to hold before a figure below it means anything."""
    measured = len(primary)
    unanimous = sum(
        1 for rows in primary.values() if len({r["register"] for r in rows}) == 1
    )
    energy_unanimous = sum(
        1 for rows in primary.values() if len({is_high(r) for r in rows}) == 1
    )
    print("judge reliability")
    print(f"  repeat agreement on register: {unanimous}/{measured} texts unanimous "
          f"across {config.JUDGE_PASSES} passes")
    if measured and unanimous / measured < config.AGREEMENT_THRESHOLD:
        print(f"  BELOW the {config.AGREEMENT_THRESHOLD:.0%} threshold — "
              f"treat every register figure below as unreliable")
    print(f"  repeat agreement on energy (level >= {config.ENERGY_HIGH_THRESHOLD}): "
          f"{energy_unanimous}/{measured} texts unanimous")
    if measured and energy_unanimous / measured < config.ENERGY_AGREEMENT_THRESHOLD:
        print(f"  BELOW the {config.ENERGY_AGREEMENT_THRESHOLD:.0%} threshold — "
              f"treat every energy figure below as unreliable")

    for axis, extract in (("register", lambda rows: Counter(
            r["register"] for r in rows).most_common(1)[0][0]),
            ("energy", lambda rows: majority(rows, is_high))):
        agree = sum(
            1
            for identifier, rows in primary.items()
            if identifier in cross
            and extract(rows) == extract([cross[identifier]])
        )
        print(f"  agreement with {config.CROSS_JUDGE_MODEL} on {axis}: "
              f"{agree}/{len(cross)}")


def report_controls(primary):
    """The hand-written texts, one line each, against the labels they carry.

    Energy is what decides between wordings in this round, so the controls that
    matter most are the ones built to break a judge that counts surface
    markers: a report voice with an exclamation mark on every sentence, and a
    reply full of empathy written flat.
    """
    controls = sorted(
        (identifier, rows)
        for identifier, rows in primary.items()
        if identifier[0].startswith("control-")
    )
    correct = Counter()
    total = Counter()
    print()
    print("controls (hand-written, known labels)")
    for identifier, rows in controls:
        got = {
            "register": Counter(r["register"] for r in rows).most_common(1)[0][0],
            "energy_high": majority(rows, is_high),
            "empathy": majority(rows, lambda r: r.get("empathy_padding")),
        }
        expected = {
            "register": rows[0].get("expected"),
            "energy_high": rows[0].get("expected_energy_high"),
            "empathy": rows[0].get("expected_empathy"),
        }
        levels = [r.get("energy_level") for r in rows]
        marks = []
        for axis in ("register", "energy_high", "empathy"):
            if expected[axis] is None:
                continue
            total[axis] += 1
            hit = got[axis] == expected[axis]
            correct[axis] += hit
            marks.append(f"{axis}={got[axis]}{'' if hit else f' MISS(want {expected[axis]})'}")
        print(f"  {identifier[0]:<26} levels={levels}  " + "  ".join(marks))
    print("  correct: " + "  ".join(
        f"{axis} {correct[axis]}/{total[axis]}" for axis in sorted(total)))


def main():
    controls_only = "--controls-only" in sys.argv
    judgements = [
        j for j in load(CONTROL_JUDGEMENTS_FILE if controls_only else JUDGEMENTS_FILE)
        if "error" not in j
    ]

    primary = defaultdict(list)
    cross = {}
    for row in judgements:
        if row["judge_model"] == config.JUDGE_MODEL:
            primary[key(row)].append(row)
        else:
            cross[key(row)] = row

    # Keys judged fewer times than planned are excluded outright rather than
    # contributing a majority drawn from a smaller vote than everything else.
    under_judged = [i for i, rows in primary.items() if len(rows) != config.JUDGE_PASSES]
    for identifier in under_judged:
        del primary[identifier]

    report_reliability(primary, cross)
    if under_judged:
        print(f"  excluded from every figure below: {len(under_judged)} texts "
              f"without {config.JUDGE_PASSES} successful passes")
    report_controls(primary)
    if controls_only:
        return

    replies = {key(r): r for r in load(REPLIES_FILE) if "error" not in r}

    by_cell = defaultdict(list)
    by_cell_style = defaultdict(list)
    by_cell_turn = defaultdict(dict)
    for identifier, rows in primary.items():
        if identifier[0].startswith("control-"):
            continue
        cell, _, _ = identifier
        levels = [r["energy_level"] for r in rows if isinstance(r.get("energy_level"), int)]
        entry = {
            "register": Counter(r["register"] for r in rows).most_common(1)[0][0],
            "tameguchi": majority(rows, lambda r: r.get("tameguchi")),
            "energy_high": majority(rows, is_high),
            "energy_level": sum(levels) / len(levels) if levels else None,
            "empathy": majority(rows, lambda r: r.get("empathy_padding")),
        }
        by_cell[cell].append(entry)
        by_cell_style[(cell, replies[identifier].get("style"))].append(entry)
        by_cell_turn[cell][(identifier[1], identifier[2])] = entry["register"]

    print()
    print("register by cell")
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        kansai = sum(1 for r in rows if r["register"] == "kansai")
        tame = sum(1 for r in rows if r["tameguchi"])
        breakdown = " ".join(
            f"{k}={v}" for k, v in sorted(Counter(r["register"] for r in rows).items())
        )
        print(f"  {cell:<22} kansai {kansai:>3}/{len(rows):<3} "
              f"tameguchi {tame:>3}/{len(rows):<3}  {breakdown}")

    # Mirroring: does the user's own register change the result?
    print()
    print("register by the style of the user's turn")
    styles = ["plain", "desumasu", "casual"]
    print(f"  {'cell':<22} " + " ".join(f"{s:>10}" for s in styles))
    for cell in sorted(by_cell):
        parts = []
        for style in styles:
            rows = by_cell_style.get((cell, style), [])
            if not rows:
                parts.append(f"{'-':>10}")
                continue
            kansai = sum(1 for r in rows if r["register"] == "kansai")
            parts.append(f"{kansai:>6}/{len(rows):<3}")
        print((f"  {cell:<22} " + " ".join(parts)).rstrip())

    # Decay: register per turn index, averaged over repetitions.
    print()
    print("kansai rate by turn index")
    turns = sorted({t for cell in by_cell_turn.values() for _, t in cell})
    print((f"  {'cell':<22} " + " ".join(f"t{t:<3}" for t in turns)).rstrip())
    for cell in sorted(by_cell_turn):
        parts = []
        for turn in turns:
            values = [v for (_, t), v in by_cell_turn[cell].items() if t == turn]
            hits = sum(1 for v in values if v == "kansai")
            parts.append(f"{hits}/{len(values)}" if values else "-")
        print((f"  {cell:<22} " + " ".join(f"{p:<4}" for p in parts)).rstrip())

    # First person. Substring occurrences only — whether a match outside the
    # specified set is a violation is a judgement made by reading it.
    print()
    print("first person (raw substring occurrences; matches need reading)")
    for cell in sorted(by_cell):
        joined = "\n".join(r["text"] for k, r in replies.items() if k[0] == cell)
        specified = sum(joined.count(p) for p in config.SPECIFIED_PRONOUNS)
        other = {p: joined.count(p) for p in config.OTHER_PRONOUNS if joined.count(p)}
        print(f"  {cell:<22} specified={specified:<4} " +
              (f"other={other}" if other else "other=none"))

    # Energy. The axis this round is decided on, so the judge's call, the mean
    # of the ordinal behind it and the independent marker count are printed
    # together rather than any one of them standing alone.
    print()
    print("energy")
    print(f"  {'cell':<22} {'high':>9} {'mean level':>11} {'markers/reply':>14}")
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        high = sum(1 for r in rows if r["energy_high"])
        levels = [r["energy_level"] for r in rows if r["energy_level"] is not None]
        mean = sum(levels) / len(levels) if levels else float("nan")
        texts = [r["text"] for k, r in replies.items() if k[0] == cell]
        markers = sum(len(ENERGY_MARKERS.findall(t)) for t in texts) / max(len(texts), 1)
        print(f"  {cell:<22} {high:>5}/{len(rows):<3} {mean:>11.2f} {markers:>14.1f}")

    # Energy by the style of the user's turn. The seven technical turns are not
    # where brightness is wanted -- an explanation of what squash merge costs
    # has no cheerful version -- so the aggregate above dilutes the three casual
    # turns with seven that no wording is trying to move.
    print()
    print("energy (level >= 2) by the style of the user's turn")
    print(f"  {'cell':<22} " + " ".join(f"{s:>10}" for s in styles))
    for cell in sorted(by_cell):
        parts = []
        for style in styles:
            rows = by_cell_style.get((cell, style), [])
            if not rows:
                parts.append(f"{'-':>10}")
                continue
            high = sum(1 for r in rows if r["energy_high"])
            parts.append(f"{high:>6}/{len(rows):<3}")
        print((f"  {cell:<22} " + " ".join(parts)).rstrip())

    # Empathy padding. Not a target — printed to show whether a wording bought
    # its brightness by inventing shared feeling or experience, which the rules
    # forbid on accuracy grounds regardless of how it scores here.
    # Split by style for the same reason as energy, and one more: two of the
    # three casual turns ask the assistant how it feels. Empathy there is
    # answering the question, not padding, so the plain and desumasu columns
    # are where an invented rapport would show.
    print()
    print("empathy padding (not a target; a side effect to watch)")
    print(f"  {'cell':<22} {'all':>10} " + " ".join(f"{s:>10}" for s in styles))
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        parts = [f"{sum(1 for r in rows if r['empathy']):>6}/{len(rows):<3}"]
        for style in styles:
            subset = by_cell_style.get((cell, style), [])
            if not subset:
                parts.append(f"{'-':>10}")
                continue
            parts.append(f"{sum(1 for r in subset if r['empathy']):>6}/{len(subset):<3}")
        print((f"  {cell:<22} " + " ".join(parts)).rstrip())

    cost = sum(r.get("cost_usd") or 0 for r in replies.values())
    print()
    print(f"generation cost reported at list price: ${cost:.2f}")


if __name__ == "__main__":
    main()
