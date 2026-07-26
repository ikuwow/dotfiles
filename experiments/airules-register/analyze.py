"""Aggregate the recorded judgements into the reported figures.

Reports, in order: how much of the recorded data reached the figures, whether
the judge is trustworthy on this run, the hand-written controls it was checked
against, then register, mirroring, decay, first person, energy and empathy.

`--controls-only` reads `judgements-controls.jsonl` and stops after the controls
section, which is the gate run before any replies are generated.

Fields the judge produces are read with `[]` rather than `.get()` throughout. A
missing one means the rubric and the parser disagree, and the useful outcome is
a crash naming the key -- a default would be counted as a real vote, land in the
denominator, and register as unanimous agreement on the way through.
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
CELL_WIDTH = 26
# Derived rather than written out, so a style added to config.PROBE_TURNS cannot
# silently vanish from the tables that split on it. First-appearance order, which
# is the order the probe set introduces them in.
STYLES = list(dict.fromkeys(style for style, _ in config.PROBE_TURNS))


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def key(row):
    return (row["cell"], row["rep"], row["turn"])


def is_high(row):
    """The judge's ordinal collapsed to the boolean the cells are compared on."""
    return row["energy_level"] >= config.ENERGY_HIGH_THRESHOLD


def majority(rows, predicate):
    return sum(1 for r in rows if predicate(r)) > len(rows) / 2


def report_sample(judgements, primary):
    """What reached the figures, before any figure.

    A text whose passes all failed never enters `primary`, so it cannot appear
    in a count of what was excluded from `primary`. Reporting against the keys
    present in the file is the only way a wholesale judging failure shows up as
    something other than every ratio quietly resting on a smaller sample.
    """
    all_keys = {key(row) for row in judgements}
    ok = set(primary)
    print("sample")
    print(f"  texts in the judgements file: {len(all_keys)}")
    print(f"  with {config.JUDGE_PASSES} successful primary passes: {len(ok)}")
    missing = len(all_keys) - len(ok)
    if missing:
        print(f"  EXCLUDED from every figure below: {missing} texts")
    if not ok:
        sys.exit("no text has a complete set of primary passes; nothing to report")


def report_reliability(primary, cross):
    """Everything that has to hold before a figure below it means anything."""
    measured = len(primary)
    unanimous = sum(
        1 for rows in primary.values() if len({r["register"] for r in rows}) == 1
    )
    energy_unanimous = sum(
        1 for rows in primary.values() if len({is_high(r) for r in rows}) == 1
    )
    print()
    print("judge reliability")
    print(f"  repeat agreement on register: {unanimous}/{measured} texts unanimous "
          f"across {config.JUDGE_PASSES} passes")
    if unanimous / measured < config.AGREEMENT_THRESHOLD:
        print(f"  BELOW the {config.AGREEMENT_THRESHOLD:.0%} threshold — "
              f"treat every register figure below as unreliable")
    print(f"  repeat agreement on energy (level >= {config.ENERGY_HIGH_THRESHOLD}): "
          f"{energy_unanimous}/{measured} texts unanimous")
    if energy_unanimous / measured < config.ENERGY_AGREEMENT_THRESHOLD:
        print(f"  BELOW the {config.ENERGY_AGREEMENT_THRESHOLD:.0%} threshold — "
              f"treat every energy figure below as unreliable")

    # Only texts the primary judge completed can be compared, so they are also
    # the denominator. Counting the rest as disagreements would report a judging
    # failure as a disagreement between models, which is the wrong alarm.
    comparable = [i for i in primary if i in cross]
    for axis, extract in (("register", lambda rows: Counter(
            r["register"] for r in rows).most_common(1)[0][0]),
            ("energy", lambda rows: majority(rows, is_high))):
        agree = sum(
            1 for i in comparable if extract(primary[i]) == extract([cross[i]])
        )
        print(f"  agreement with {config.CROSS_JUDGE_MODEL} on {axis}: "
              f"{agree}/{len(comparable)}")
    if len(cross) != len(comparable):
        print(f"  not comparable: {len(cross) - len(comparable)} texts judged by "
              f"{config.CROSS_JUDGE_MODEL} but not completed by the primary judge")


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
    axes = ("register", "energy_high", "empathy")
    correct = Counter()
    print()
    print("controls (hand-written, known labels)")
    for identifier, rows in controls:
        got = {
            "register": Counter(r["register"] for r in rows).most_common(1)[0][0],
            "energy_high": majority(rows, is_high),
            "empathy": majority(rows, lambda r: r["empathy_padding"]),
        }
        # Every control carries every label. A missing one used to drop that axis
        # from the score silently, so a mistyped key in controls.jsonl shrank the
        # gate while it went on printing a confident-looking total.
        expected = {
            "register": rows[0]["expected"],
            "energy_high": rows[0]["expected_energy_high"],
            "empathy": rows[0]["expected_empathy"],
        }
        marks = []
        for axis in axes:
            hit = got[axis] == expected[axis]
            correct[axis] += hit
            marks.append(f"{axis}={got[axis]}"
                         + ("" if hit else f" MISS(want {expected[axis]})"))
        levels = [r["energy_level"] for r in rows]
        print(f"  {identifier[0]:<{CELL_WIDTH}} levels={levels}  " + "  ".join(marks))
    total = len(controls)
    print("  correct: " + "  ".join(f"{axis} {correct[axis]}/{total}" for axis in axes))
    if any(correct[axis] != total for axis in axes):
        print("  GATE FAILED — the judge does not reproduce the hand-written labels; "
              "fix the rubric before generating replies")
    else:
        print("  gate passed")


def main():
    if config.JUDGE_PASSES % 2 == 0:
        sys.exit("config.JUDGE_PASSES must be odd; majority() resolves a tie to False")

    controls_only = "--controls-only" in sys.argv
    judgements = load(CONTROL_JUDGEMENTS_FILE if controls_only else JUDGEMENTS_FILE)
    succeeded = [j for j in judgements if "error" not in j]

    primary = defaultdict(list)
    cross = {}
    for row in succeeded:
        if row["judge_model"] == config.JUDGE_MODEL:
            primary[key(row)].append(row)
        else:
            cross[key(row)] = row

    # Keys judged fewer times than planned are excluded outright rather than
    # contributing a majority drawn from a smaller vote than everything else.
    for identifier in [i for i, rows in primary.items()
                       if len(rows) != config.JUDGE_PASSES]:
        del primary[identifier]

    report_sample(judgements, primary)
    report_reliability(primary, cross)
    report_controls(primary)
    if controls_only:
        return

    replies = {key(r): r for r in load(REPLIES_FILE) if "error" not in r}

    cells = defaultdict(list)
    by_cell = defaultdict(list)
    by_cell_style = defaultdict(list)
    by_cell_turn = defaultdict(dict)
    for identifier, rows in sorted(primary.items()):
        if identifier[0].startswith("control-"):
            continue
        cell, rep, turn = identifier
        entry = {
            "register": Counter(r["register"] for r in rows).most_common(1)[0][0],
            "tameguchi": majority(rows, lambda r: r["tameguchi"]),
            "energy_high": majority(rows, is_high),
            "energy_level": sum(r["energy_level"] for r in rows) / len(rows),
            "empathy": majority(rows, lambda r: r["empathy_padding"]),
        }
        # The text is carried alongside the judgement so that the marker count
        # and the first-person count are computed over the same texts as the
        # judge's call. Read from `replies` directly they would include texts
        # excluded above, and the energy table's whole point is that its three
        # columns cross-check each other.
        cells[cell].append(replies[identifier]["text"])
        by_cell[cell].append(entry)
        by_cell_style[(cell, replies[identifier]["style"])].append(entry)
        by_cell_turn[cell][(rep, turn)] = entry["register"]

    print()
    print("register by cell")
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        kansai = sum(1 for r in rows if r["register"] == "kansai")
        tame = sum(1 for r in rows if r["tameguchi"])
        breakdown = " ".join(
            f"{k}={v}" for k, v in sorted(Counter(r["register"] for r in rows).items())
        )
        print(f"  {cell:<{CELL_WIDTH}} kansai {kansai:>3}/{len(rows):<3} "
              f"tameguchi {tame:>3}/{len(rows):<3}  {breakdown}")

    # Mirroring: does the user's own register change the result?
    print()
    print("register by the style of the user's turn")
    print(f"  {'cell':<{CELL_WIDTH}} " + " ".join(f"{s:>10}" for s in STYLES))
    for cell in sorted(by_cell):
        parts = []
        for style in STYLES:
            rows = by_cell_style.get((cell, style), [])
            if not rows:
                parts.append(f"{'-':>10}")
                continue
            kansai = sum(1 for r in rows if r["register"] == "kansai")
            parts.append(f"{kansai:>6}/{len(rows):<3}")
        print((f"  {cell:<{CELL_WIDTH}} " + " ".join(parts)).rstrip())

    # Decay: register per turn index, averaged over repetitions.
    print()
    print("kansai rate by turn index")
    turns = sorted({t for cell in by_cell_turn.values() for _, t in cell})
    print((f"  {'cell':<{CELL_WIDTH}} " + " ".join(f"t{t:<3}" for t in turns)).rstrip())
    for cell in sorted(by_cell_turn):
        parts = []
        for turn in turns:
            values = [v for (_, t), v in by_cell_turn[cell].items() if t == turn]
            hits = sum(1 for v in values if v == "kansai")
            parts.append(f"{hits}/{len(values)}" if values else "-")
        print((f"  {cell:<{CELL_WIDTH}} " + " ".join(f"{p:<4}" for p in parts)).rstrip())

    # First person. Substring occurrences only — whether a match outside the
    # specified set is a violation is a judgement made by reading it.
    print()
    print("first person (raw substring occurrences; matches need reading)")
    for cell in sorted(by_cell):
        joined = "\n".join(cells[cell])
        specified = sum(joined.count(p) for p in config.SPECIFIED_PRONOUNS)
        other = {p: joined.count(p) for p in config.OTHER_PRONOUNS if joined.count(p)}
        print(f"  {cell:<{CELL_WIDTH}} specified={specified:<4} " +
              (f"other={other}" if other else "other=none"))

    # Energy. The axis this round is decided on, so the judge's call, the mean
    # of the ordinal behind it and the independent marker count are printed
    # together rather than any one of them standing alone.
    print()
    print("energy")
    print(f"  {'cell':<{CELL_WIDTH}} {'high':>9} {'mean level':>11} {'markers/reply':>14}")
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        high = sum(1 for r in rows if r["energy_high"])
        mean = sum(r["energy_level"] for r in rows) / len(rows)
        markers = sum(len(ENERGY_MARKERS.findall(t)) for t in cells[cell]) / len(rows)
        print(f"  {cell:<{CELL_WIDTH}} {high:>5}/{len(rows):<3} "
              f"{mean:>11.2f} {markers:>14.1f}")

    # Energy by the style of the user's turn. The seven technical turns are not
    # where brightness is wanted -- an explanation of what squash merge costs
    # has no cheerful version -- so the aggregate above dilutes the three casual
    # turns with seven that no wording is trying to move.
    print()
    print(f"energy (level >= {config.ENERGY_HIGH_THRESHOLD}) "
          f"by the style of the user's turn")
    print(f"  {'cell':<{CELL_WIDTH}} " + " ".join(f"{s:>10}" for s in STYLES))
    for cell in sorted(by_cell):
        parts = []
        for style in STYLES:
            rows = by_cell_style.get((cell, style), [])
            if not rows:
                parts.append(f"{'-':>10}")
                continue
            high = sum(1 for r in rows if r["energy_high"])
            parts.append(f"{high:>6}/{len(rows):<3}")
        print((f"  {cell:<{CELL_WIDTH}} " + " ".join(parts)).rstrip())

    # Split by style for the same reason as energy, and one more: two of the
    # three casual turns ask the assistant how it feels. Empathy there is
    # answering the question, not padding, so the plain and desumasu columns
    # are where an invented rapport would show.
    print()
    print("empathy padding (not a target; a side effect to watch)")
    print(f"  {'cell':<{CELL_WIDTH}} {'all':>10} " + " ".join(f"{s:>10}" for s in STYLES))
    for cell in sorted(by_cell):
        rows = by_cell[cell]
        parts = [f"{sum(1 for r in rows if r['empathy']):>6}/{len(rows):<3}"]
        for style in STYLES:
            subset = by_cell_style.get((cell, style), [])
            if not subset:
                parts.append(f"{'-':>10}")
                continue
            parts.append(f"{sum(1 for r in subset if r['empathy']):>6}/{len(subset):<3}")
        print((f"  {cell:<{CELL_WIDTH}} " + " ".join(parts)).rstrip())

    cost = sum(r.get("cost_usd") or 0 for r in replies.values())
    print()
    print(f"generation cost reported at list price: ${cost:.2f}")


if __name__ == "__main__":
    main()
