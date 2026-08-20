# pr-selfcheck run-to-run agreement

Measures how much of `/pr-selfcheck`'s output is reproducible when nothing
about its input changes. Tracked in ikuwow/dotfiles#369.

Three runs against PR #367 on 2026-08-20 disagreed about a defect in its body:
one reported it as a `Fix`, two did not mention it and reported the diff fully
accounted for. A single run therefore cannot be treated as evidence, and every
`PASS` recorded while iterating on #366 and #367 carries less than it appeared
to. This round asks how large that effect is.

## What comes out of a round

- Verdict agreement: the `PASS` / `NEEDS_IMPROVEMENT` split across runs, which
  needs no interpretation of what any run said
- Defect agreement: for each defect any run reported, how many runs reported
  it. A defect that only one run in ten reaches is the measurement that makes
  a single run unusable as a gate
- Evidence routes: what each run had in hand, read off its own tool results

The third table is what decides where a fix belongs. A run that held a source
and reported no defect judged differently from a run that reported one; a run
that never held the source could not have judged at all. Only the second kind
of miss is answerable by prescribing collection in the skill's steps.

## Design

The target is a merged PR, so its body, its diff and its head commit are
frozen and every run sees byte-identical input. An open PR cannot serve: two of
the runs in #369 reported the body changing between their own fetches.

`/pr-selfcheck` is invoked as a session invokes it — the slash command, under
this repository's own settings, with no override of the model, the effort
level, or the permission mode. The skill's own frontmatter decides how the
check runs, and overriding any of it measures a detector that is not the
deployed one.

Runs are sequential. The check's step 3 runs `git fetch origin pull/<n>/head`
and reads through that ref, which concurrent runs would race on.

A round refuses to start unless the working tree is clean. One run in #369
declined to read a file after judging the tree's uncommitted changes to belong
to another session, which makes uncommitted state an input to the detector
rather than a neutral background.

Grouping findings into defects is a judgement, so `judge.py` takes three
passes over the same input and treats two findings as one defect when at least
two passes group them together. Per-defect disagreement between passes is
reported next to each row, so a grouping that held in only one pass cannot
pass as settled.

## What this can and cannot establish

The invocation reproduces the deployed condition on the axis that matters
most. `context: fork` means "the skill content becomes the prompt that drives
the subagent. It won't have access to your conversation history"
([skills reference](https://code.claude.com/docs/en/skills)), so a check
launched from a session that just authored the PR starts as cold as one
launched from a harness. What the check knows is what its own steps collect.

One documented difference does not reach the check. Under `-p`, Claude Code
waits for a forked skill's result instead of backgrounding it, and a
backgrounded fork runs with the narrower tool set that applies to background
subagents (same reference). Every tool the check uses — `Bash`, `Read`,
`Grep`, `Glob`, `WebFetch` — is in that narrower set, so the check's tool pool
is the same either way.

Two conditions are local to the machine that ran the round.

The evidence route that separated the one #369 run reporting the unaccounted
hunk is `ikuwowfiles/pr-guidelines-reformat-check.md`, which is gitignored. A
round run from a fresh clone has no such file, and its `read_record` column
would be empty for a reason that has nothing to do with the checker.

The check writes intermediate files to `/tmp` under names it chooses, and a
later run can find one a previous run left. The round does not isolate this.

Runs are on `claude-sonnet-5`, which is what the skill's frontmatter selects.
A figure here does not transfer to the same skill under a different model.

## Running a round

```
python3 run.py       # N runs, appends to round1/runs.jsonl, resumable
python3 extract.py   # reports and transcripts -> round1/findings.jsonl
python3 judge.py     # groups findings into defects -> round1/clusters.json
python3 analyze.py   # the three tables
```

`run.py` skips runs already in `runs.jsonl`, so a round interrupted by a rate
limit or a killed process restarts with the same command.

Both transcripts are copied out of `~/.claude/projects` into `round1/runs/`
as each run completes, because Claude Code prunes that directory and the
analysis has to stay reproducible from the committed files alone.
