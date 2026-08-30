# Implementer Dispatch

The parent-side procedure for a git-workflow run whose implementation
step is handed to the `implementer` subagent. Whether to delegate at
all is decided by the implementation-delegation rule; this file starts
from the point where the answer is yes.

## Before dispatching

- Complete branch setup — pull the default branch, create the feature
  branch — before dispatching, since the subagent implements on the
  branch it is handed
- When the branch needs newer default-branch commits, the parent
  merges them and re-dispatches

## Writing the brief

- Name the files the change touches and the entry points to start from
- State the verification scope and cadence once as an outcome ("the
  package's tests and lint pass before each commit"), not as per-step
  instructions to run a command after individual edits
- Prescribe a verification command only after confirming it runs on
  this host; when a check only runs in CI, say so and name the job

## What a dispatch does by default

- Every implementer dispatch, single or parallel, ends with the branch
  pushed, a draft PR open, and a time-bounded CI watch
  - To stop it at local commits, put "do not push" or "commits only"
    in the brief

## While it runs

- A mid-run message from an implementer (push landed, entering a CI
  fix round) is visibility only and needs no reply
  - The branch is still moving, so review and Phase 1 checks wait for
    the completion report

## When it returns

- When an implementer returns with CI still in flight, go straight to
  the Phase 1 checks instead of waiting on it
- When the implementer opened the PR, replace the placeholder body and
  drop the `WIP:` prefix from the title before running `/pr-selfcheck`
  - The body is a fixed stub carrying no content, and the title is a
    real one-line summary that only needs the prefix removed
- Always read the completion report and commit list (`git log --stat`)
- Read the final diff once (`git diff main...`) by default
- Deep manual re-review only when the report flags deviations or
  ambiguities, verification results are weak, or the change touches
  risky areas
- Systematic review stays with the PR review pipeline (pr-selfcheck /
  pr-review-toolkit)

## CI failures

- Hand a CI failure back to the same implementer, addressed by the
  name or agentId from its spawn result, instead of dispatching a
  fresh one or taking the fix loop into the parent
  - One handback per PR: the implementer gets a single fix round per
    dispatch, and a failure that survives the handback is the parent's
    call

## Multi-PR plans

- When an approved plan decomposes into multiple PRs with no
  interdependencies (no merge-order dependency, no file/section
  overlap that would conflict when the sibling merges first), run the
  git-workflow skill once per PR in parallel, each dispatching its own
  implementer
- Send the parallel implementer Agent calls in a single message so
  they execute concurrently
- Create one worktree and branch per parallel implementer before
  dispatching, since parallel implementers require worktree isolation
  per the implementer agent's Concurrency rule
- In projects that prohibit worktrees, fall back to sequential
  single-implementer dispatch
- Dependent PR chains (B rebases on A's merge, C reviews A's design
  decision) stay sequential
- Each implementer pushes its own branch and opens its own draft PR,
  so the parent monitors one PR per dispatched implementer
- Apply the "When it returns" steps once per dispatched implementer
