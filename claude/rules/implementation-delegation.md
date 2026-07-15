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

- Complete branch setup (pull the default branch, create the feature
  branch — one worktree+branch per implementer when running parallel
  dispatch) before dispatching; the subagent must not create branches
  or worktrees

## Parallel dispatch for multi-PR plans

- When an approved plan decomposes into multiple PRs with no
  interdependencies (no merge-order dependency, no file/section
  overlap that would conflict when the sibling merges first), run
  the git-workflow skill once per PR in parallel, each dispatching
  its own implementer
- Send the parallel implementer Agent calls in a single message so
  they execute concurrently
- Parallel implementers require worktree isolation per the implementer
  agent's Concurrency rule; in projects that prohibit worktrees, fall
  back to sequential single-implementer dispatch
- Dependent PR chains (B rebases on A's merge, C reviews A's design
  decision) stay sequential
- The parent still owns push, PR creation, review, and monitor for
  each PR; the implementer's role is unchanged (implement + local
  commits in its assigned worktree)
- Apply the section below once per dispatched implementer

## Review of the subagent's work

- Always read the completion report and commit list (`git log --stat`)
- Read the final diff once (`git diff main...`) by default
- Deep manual re-review only when the report flags deviations or
  ambiguities, verification results are weak, or the change touches
  risky areas
- Systematic review stays with the PR review pipeline (pr-selfcheck /
  pr-review-toolkit)
