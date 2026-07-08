# Implementation Delegation

When to hand implementation work to the `implementer` subagent instead
of implementing in the main session.

## Trigger

- When an approved plan exists, or the user approves a concrete change
  set, delegate the implementation to the `implementer` subagent by
  default
- This applies equally to direct-spec tasks that never went through
  plan mode

## Exceptions (implement inline)

- A one-shot edit of a few lines
- Work that needs the parent's live conversation context and would be
  lossy to re-brief
- Exploratory scope or undecided design (belongs in the parent session
  or a Plan agent first)

## Ordering

- Complete branch setup (git workflow Step 1) before dispatching; the
  subagent must not create branches or worktrees

## Review of the subagent's work

- Always read the completion report and commit list (`git log --stat`)
- Read the final diff once (`git diff main...`) by default
- Deep manual re-review only when the report flags deviations or
  ambiguities, verification results are weak, or the change touches
  risky areas
- Systematic review stays with the PR review pipeline (pr-selfcheck /
  pr-review-toolkit)
