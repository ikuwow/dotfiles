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
  branch) before dispatching; the subagent must not create branches or
  worktrees
- Applies to single-implementer dispatch. Multi-PR parallel dispatch
  follows the next section instead

## Parallel dispatch for multi-PR plans

- When an approved plan decomposes into multiple PRs with no
  interdependencies (each can be merged independently against the
  default branch), dispatch one implementer per PR in parallel (send
  the Agent calls in a single message)
- Each implementer runs the git-workflow skill end-to-end for its own
  PR — creating its own worktree and branch. The parent does NOT
  pre-create branches or worktrees in this mode (the Ordering rule
  above is overridden)
- PRs with a dependency chain (B rebases on A's merge, C reviews A's
  design decision) stay sequential
- In projects whose rules prohibit worktrees, parallel dispatch is
  unavailable — fall back to sequential single-implementer dispatch
- Review each PR independently per the section below

## Review of the subagent's work

- Always read the completion report and commit list (`git log --stat`)
- Read the final diff once (`git diff main...`) by default
- Deep manual re-review only when the report flags deviations or
  ambiguities, verification results are weak, or the change touches
  risky areas
- Systematic review stays with the PR review pipeline (pr-selfcheck /
  pr-review-toolkit)
