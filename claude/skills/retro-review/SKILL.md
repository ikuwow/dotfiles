---
name: retro-review
description: Batch review of accumulated retro-notes; clusters findings by failure mechanism, diagnoses rules, and turns approved fixes into PRs. TRIGGER when the user invokes /retro-review or asks to batch-analyze retro notes.
---

# Retro Review

Batch-analyzes the retro-note records accumulated on this machine,
clusters them by failure mechanism, diagnoses the rule set, and turns
approved fixes into PRs.

Data contract with retro-note: notes are append-only JSONL files at
`${XDG_DATA_HOME:-$HOME/.local/share}/claude/retrospective/notes/<project-slug>/YYYY-MM.jsonl`
(record schema defined in the retro-note skill). Review artifacts live
next to them under `.../retrospective/reviews/<cycle>/`. Both are
machine-local by design; rule fixes propagate across machines through
the dotfiles repo.

## When to run

Worth invoking when roughly 30+ unreviewed findings have accumulated
across projects, or when a high-severity failure pattern feels like it
is recurring. No fixed cadence.

## Step 1: Scope

1. List all note files under `notes/<project>/*.jsonl`.
1. Read every `reviews/*/scope.json` from previous cycles. For each
   note file, lines beyond the maximum `lines_covered` recorded for it
   are unreviewed. A file with no scope entry (or no `reviews/`
   directory at all) is entirely unreviewed.
1. Count the unreviewed findings (sum of `findings | length` over
   unreviewed lines) with jq and report the count to the user before
   doing anything else. Zero: report and stop. Fewer than ~10: say
   that deferring is reasonable and ask whether to continue.

## Step 2: Flatten

Set `cycle` to today's date (`YYYY-MM-DD`; a same-day rerun overwrites
its own artifacts). Create the workdir
`.../retrospective/reviews/<cycle>/`.

Flatten the unreviewed lines into `findings.jsonl` in the workdir, one
record per finding:

```json
{"row": 1, "id": "<project>:<session_id first 8>:<ts>:<finding index>", "project": "...", "ts": "...", "task": "...", "severity": "...", "feedback_target": "...", "behavior": "...", "root": "..."}
```

- `ts` is part of the id: session_id alone collides when one session
  appends multiple records
- `row` is the 1-based line number in this cycle's findings.jsonl

Then write `scope.json`: `[{"project": ..., "file": ..., "lines_covered": N}]`
where `lines_covered` is each note file's total line count as of this
flatten (previously covered plus newly covered).

## Step 3: Normalize targets (subagent)

Dispatch one sonnet subagent to map each finding's free-text
`feedback_target` to one or two canonical IDs:

- `AIRULES.md#<section name>`
- `rules/<filename>`
- `skills/<name>`
- `project:<name>/CLAUDE.md`
- `other:<short label>` only when nothing fits

The agent must list the real assets first (AIRULES.md section names,
`claude/rules/`, `claude/skills/` in the dotfiles repo) before mapping,
write `target-map.jsonl` (`{row, id, targets[]}`) to the workdir, and
report a frequency table plus any mappings it was unsure about.

## Step 4: Cluster (subagent)

Dispatch one sonnet subagent (two independent ones plus a reconcile
pass when findings exceed ~60) to cluster all findings by the mechanism
similarity of their `root` fields, explicitly ignoring
`feedback_target`. Give it `${CLAUDE_SKILL_DIR}/clusters.md` as the
starting taxonomy; proposing new clusters or splits is allowed.

Output: `assignment.jsonl` in the workdir
(`{row, id, ts, severity, cluster, disputed, note}`), plus a count
table and the disputed/borderline list in its report.

## Step 5: Review and diagnose (main session)

Do not delegate this step: it needs the rule files already in the main
session context and cross-rule judgment.

1. Spot-review disputed/borderline assignments against the boundary
   criteria in `clusters.md`; correct `assignment.jsonl` where needed.
1. Effect measurement: read previous cycles' `actions.jsonl`. For each
   prior rule-edit and watch action, report whether its cluster
   recurred in this cycle's data (count and severity). This output is
   mandatory — without it the feedback loop does not close.
1. Diagnose each cluster: rule-absent / rule-weak / rule-not-followed.
1. Decide a disposition per cluster: rule-edit / skill-step / hook /
   watch / accept / planned. Weigh cost of failure: cheap
   self-correcting failures lean accept; failures that reach persisted
   artifacts, infrastructure, or user-facing claims lean structural
   fixes.
1. Write `report.md` to the workdir: cluster table (counts, severity
   mix, diagnosis, disposition), effect-measurement results, key
   observations, and proposed actions in priority order.

## Step 6: Checkpoint with the user

Present the report summary and the proposed action list. Creating PRs
and editing rules are external mutations — proceed only with the
actions the user approves. Record deferred or declined proposals as
planned/accept entries in Step 8.

## Step 7: Execute approved actions

One action = one PR. For each approved action, invoke the git-workflow
skill (branch, edit, draft PR, CI and review phases). Rule edits follow
the rule-editing section of AIRULES.md (integrate into the affected
instruction, positive form, one sentence per bullet). Record which
review findings were adopted or declined, and why, in `report.md`.

## Step 8: Persist lifecycle

Append one record per action — including watch, accept, and planned
dispositions — to the workdir's `actions.jsonl`:

```json
{"action_id": "<cycle>-A<n>", "cluster": "...", "disposition": "...", "target": "...", "pr": "<owner/repo#N or null>", "date": "...", "findings": [{"row": 1, "id": "..."}], "note": "..."}
```

Use the Write tool for new files; for appends, use the retro-note
pattern (Write a pretty-printed temp file, then a single
`jq -c '.' <tmp> >> <target>` Bash command).

## Step 9: Report

One short summary: N findings reviewed, M clusters, effect-measurement
headline, K actions with PR URLs.
