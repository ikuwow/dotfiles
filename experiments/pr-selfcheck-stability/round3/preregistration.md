# Round 3 and 4 preregistration

Written and committed before either round runs, so the criteria below are
fixed independently of what the runs report.

## What is being measured

A variant of the `Scoped` rule in `pr-guidelines.md` binds the unit the
property is judged at. Rounds 1 and 2 show the unit is otherwise resolved to
the changed-file list in 14 of 16 runs, and the two exceptions are the two runs
that reached the defect round 2 plants.

- Round 3 runs the variant against PR #370, whose body omits a rule the diff
  adds. Read against round 2, which is the same PR under the current rules and
  reached that defect in 2 of 6 runs
- Round 4 runs the variant against PR #367, whose body carries no planted
  defect. Read against round 1, which is the same PR under the current rules
  and reported no `Fix` in 10 runs

Round 4 runs only if round 3's recall moves.

## Detection criterion for round 3

A run reaches the defect when a finding in its report names the rule the diff
adds to `Necessary` and states that the body does not account for it. Applied
mechanically: the finding text contains at least one of

- `leave its detail to the diff`
- `spelling out an added rule`
- `table row`

and the run's report is read for that finding only, not for its other content.

Two counts are reported separately, because they answer different questions and
coincided in round 2 without being the same measure.

- `reached` — the finding appears at any severity
- `blocked` — the finding appears as a `Fix`, which is what moves the verdict
  and what a gate acts on

## Outcome for round 4

The count of runs reporting at least one `Fix`, with every such `Fix` text
recorded for reading. A `Fix` here is not called a false positive by the count
alone: the body carries no planted defect, but it may carry a real one the
current rules miss, and only reading the text separates those.

## Sample size and what it can separate

Six runs per round, fixed here. One-sided Fisher against round 2's 2 of 6:

| round 3 result | p |
| --- | --- |
| 6 of 6 | 0.030 |
| 5 of 6 | 0.121 |
| 4 of 6 | 0.284 |

Six runs separate a variant that essentially closes the gap from one that does
not move it. A partial improvement is not distinguishable at this size and is
not claimed if it appears.

## Manipulation check

Before each round, one run is taken and its subagent transcript searched for
the variant's wording, confirming the changed rule text reached the check. A
round whose check fails is not analysed.

## Threats left standing

- The variant edits `pr-guidelines.md`, and both PRs under test carry diffs
  that also edit `pr-guidelines.md`, so the rulebook and the subject are the
  same file at different versions. A round against a PR that does not touch the
  rulebook would separate this and is not run
- Rounds 1 and 2 were recorded before the variant existed, so the comparison is
  between arms measured at different times rather than interleaved. Both
  baselines were taken the same day as these rounds
- Recall is measured on one defect instance of one class. A variant that moves
  it is evidence for the mechanism the rounds name, not for the check as a
  whole
