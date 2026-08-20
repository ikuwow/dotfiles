"""Report the round: verdict agreement, per-defect agreement, evidence routes.

Three tables, answering the three questions ikuwow/dotfiles#369 asks in order.

The verdict table needs no judge and no grouping -- PASS and
NEEDS_IMPROVEMENT are the checker's own two states, and their split across runs
is the coarsest statement of how stable the check is.

The defect table is the agreement measure: for each defect any run reported,
how many of the runs reported it. A defect reported by every run and a defect
reported by one are both visible here, and the second is what makes a single
run unusable as evidence.

The evidence table splits a miss. A run that had a source in hand and did not
report the defect judged differently; a run that never had it could not have
judged at all. That split decides whether the fix belongs in the skill's steps
or in its rules.
"""

import json
import os
from collections import Counter

import config


def load(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def table(header, rows):
    widths = [max(len(str(cell)) for cell in column) for column in zip(header, *rows)] \
        if rows else [len(cell) for cell in header]
    lines = ["| " + " | ".join(str(cell).ljust(width)
                               for cell, width in zip(header, widths)) + " |",
             "| " + " | ".join("-" * width for width in widths) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).ljust(width)
                                       for cell, width in zip(row, widths)) + " |")
    return "\n".join(lines)


def main():
    rows = load(config.FINDINGS_FILE)
    total = len(rows)
    print("# pr-selfcheck run-to-run agreement, PR #%d, %d runs\n" % (config.PR, total))

    print("## Verdict\n")
    verdicts = Counter(row["verdict"] for row in rows)
    print(table(["verdict", "runs"],
                [[verdict or "(unparsed)", count] for verdict, count in verdicts.most_common()]))
    malformed = [row["run"] for row in rows if row["malformed"]]
    stalled = [row["run"] for row in rows if row["outcome"] != "completed"]
    print("\nReports departing from the prescribed format: %s"
          % (", ".join("#%d" % run for run in malformed) or "none"))
    print("Runs that did not complete: %s"
          % (", ".join("#%d" % run for run in stalled) or "none"))

    counts = Counter()
    for row in rows:
        for finding in row["findings"]:
            counts[finding["severity"]] += 1
    print("\nFindings per severity across all runs: "
          + ", ".join("%s %d" % (severity, counts[severity])
                      for severity in config.SEVERITIES))
    print("Findings per run: "
          + ", ".join("#%d:%d" % (row["run"], len(row["findings"])) for row in rows))

    print("\n## Defects, by how many runs reported each\n")
    if os.path.exists(config.CLUSTERS_FILE):
        with open(config.CLUSTERS_FILE) as f:
            groups = json.load(f)["groups"]
        print(table(["runs", "of", "defect", "unaccounted hunk", "judge splits"],
                    [[len(group["runs"]), total, group["label"][:70],
                      "yes" if group["unaccounted_hunk"] else "",
                      group["pairs_not_unanimous"]] for group in groups]))
        unanimous = sum(1 for group in groups if len(group["runs"]) == total)
        singleton = sum(1 for group in groups if len(group["runs"]) == 1)
        print("\n%d defects reported by every run, %d by exactly one, %d in between."
              % (unanimous, singleton, len(groups) - unanimous - singleton))
    else:
        print("(no grouping yet -- run judge.py)")

    print("\n## What each run had in hand\n")
    names = ["read_body", "read_diff", "read_guidelines", "read_record",
             "named_record", "fetched_head"]
    print(table(["run", *names, "tool calls", "tool errors"],
                [[row["run"], *["yes" if row["signals"][name] else "" for name in names],
                  row["signals"]["tool_calls"], row["signals"]["tool_errors"]]
                 for row in rows]))
    for name in names:
        taken = sum(1 for row in rows if row["signals"][name])
        print("\n%s: %d of %d runs" % (name, taken, total))


if __name__ == "__main__":
    main()
