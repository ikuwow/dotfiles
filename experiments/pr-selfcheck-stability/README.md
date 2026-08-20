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

Each run executes in its own clone. The check's step 3 runs `git fetch origin
pull/<n>/head` and reads through that ref, so runs sharing one repository would
race on FETCH_HEAD. The clone carries the gitignored paths the check reads
(`config.MIRRORED_PATHS`) and points `origin` at the real remote, and it is
taken from the main tree at the branch that tree has checked out.

Which rules the check reads is decided by the main tree either way, because
`~/.claude/skills` resolves into it and every run recorded so far loaded
`pr-guidelines.md` through that path or the tree's own. A round measuring a
rule variant therefore requires that variant checked out in the main tree, and
for the length of the round any other session on the machine reads it too.

A round refuses to start unless the working tree is clean, and keeps it clean
while it runs. One run in #369 declined to read a file after judging the
tree's uncommitted changes to belong to another session, which makes
uncommitted state an input to the detector rather than a neutral background.
The round's own output would otherwise accumulate as untracked files and hand
each run a different tree from the one before it, so `run.py` adds the output
directory to `.git/info/exclude` and it is committed once the round is over.

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

Round 2's fixture carries one difference from the input it reconstructs. The
recovered body cites `main` as the base its verification queries ran against,
which named the merge base on 2026-08-20 and names a later commit now. Runs
that re-run those queries against today's `main` see a divergence that did not
exist when the body was written, and two of six reported it. The defect the
round measures -- a rule the diff adds and the body never names -- is decided
against the diff and the body alone, so it is unaffected; the round's other
findings are not all free of this.

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

`PRSC_ROUND` selects the round; it defaults to `round1`.

`run.py` skips runs already in `runs.jsonl`, so a round interrupted by a rate
limit or a killed process restarts with the same command. A run that exited
non-zero is recorded as failed and taken again on the next start.

Round 2 stopped at six runs rather than ten, on elapsed time. The decision was
taken before any of its reports had been read, so the stopping rule is
independent of what the runs found.

Each round's sample size is fixed in `config.ROUNDS` before the round starts.
Rounds 3 and 4 measure a variant of the `Scoped` rule and are read against the
round above them that shares a PR; `round3/preregistration.md` states what
counts as detection and fixes it before those rounds run.

Both transcripts are copied out of `~/.claude/projects` into `round1/runs/`
as each run completes, because Claude Code prunes that directory and the
analysis has to stay reproducible from the committed files alone.
