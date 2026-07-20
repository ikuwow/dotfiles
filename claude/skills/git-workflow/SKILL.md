---
name: git-workflow
description: Standard git/GitHub workflow - branch setup, implementation, draft PR creation, CI wait, code review phases, PR monitoring until merge, and post-merge cleanup. Trigger for any coding, editing, or fix task in a git repository that will end in a commit, branch, or pull request — including "just fix X" requests and documentation-only changes, not only tasks explicitly framed as workflow or release work. Also trigger when creating or updating a PR, watching CI, self-reviewing a PR, reacting to PR review comments or CI failures, or cleaning up branches after a merge.
---

# Git Workflow

Standard git/GitHub workflow for all projects.
Follow each step in order. Skip a step only when its precondition is
structurally absent (e.g., no PR exists yet).

Prerequisite: the `agynio/gh-pr-review` gh extension is installed
(used by Phase 5 review-thread reactions).

## Principles

- All steps within a single workflow run are pre-authorized by the user
  who initiated the task. Do not pause between steps to ask for
  confirmation unless blocked by an error or ambiguity. Execute the
  full flow continuously and report results at the end.
- Phase 2 code review and Phase 5 Monitor arming are pre-authorized —
  run them without pausing for confirmation. The only user decision
  point in the flow is flipping the PR from draft to ready for review.
- Signals like a small diff or personal-project scope affect how you
  weigh findings within a phase, never whether to run it. The only
  override to the pre-authorization above is an explicit user
  instruction that names a stopping point ("stop after creating the
  draft PR", "skip Phase 2 for this PR", "no Monitor"). Absent that,
  run every phase.
- Never create or edit files on the default branch. Always move into the
  worktree (or feature branch) first. Creating files before branching
  leads to redundant copy-and-delete work.
- Never modify commits that have already been pushed

## 1. Start Work

1. Pull the latest default branch:
   `git pull`
1. Create a worktree and branch (defaults to branching from origin's default branch):
   `git-worktree-create <branch-name>`
   - To branch from somewhere other than origin's default:
     `git-worktree-create <branch-name> <base>`
1. Follow the command shown in the script output to move into the worktree
1. If the project rules explicitly prohibit worktrees, create a branch only:
   `git checkout -b <branch-name>`

Note: `.worktrees/` is covered by the global gitignore.

## 2. Implement, commit, push

The implementation work for this branch happens here.

When the commit message or PR body will claim an exhaustive
replacement or update ("replaced all X with Y"), run
`git grep -n '<old pattern>'` before committing and confirm zero
remaining matches — `replace_all` misses occurrences that differ in
formatting or indentation.

## 3. Create a PR

1. Write the PR body to a fresh file under the session scratchpad
   directory using the Write tool (new filename per revision — a new
   file needs no prior Read step)
   - Follow the repository's PR template if one exists
   - Follow the PR Body Checklist
1. Create the PR as a draft:
   `gh pr create --draft --body-file <body file path>`
   - Never use `--body` for PR creation. The `#`-prefixed lines in the body
     trigger Claude Code's security pre-check, which cannot be bypassed by
     hooks. Always go through `--body-file`.
1. After creating the PR, display the PR URL to the user:
   `gh pr view --json url --jq '.url'`
1. Proceed to CI wait (step 4)

## 4. CI Wait & Review

Five phases: pass all mechanical checks, run the code review,
consolidate fixes, finalize the PR for review readiness, then watch
PR activity until merge.

### Phase 1: PR self-review + CI (parallel)

Launch both in a single assistant message so they execute concurrently:

- `/pr-selfcheck <PR number>` — PR presentation review
- `gh pr checks --watch` — CI monitoring. Run with `run_in_background: true`

If either fails:
- Fix self-review "Must Fix" / "Should Fix" items
- Fix CI failures (`gh run view --log-failed`)
- Push fixes, then re-run both until both pass

Note: `/pr-selfcheck` is a mechanical check, not a code review.
Re-running it after fixes is expected. The "single-pass" policy
applies only to the code review in Phase 2.

### Phase 2: Code review

Once Phase 1 passes, launch:

- `/pr-review-toolkit:review-pr` — multi-agent code review (CLAUDE.md
  compliance, bug detection, error handling, test coverage).
  Reports findings in the conversation, does not post PR comments.

### Phase 3: Consolidate and fix

Once the review finishes, review the results:

1. Fix issues found by the code review
1. Push fixes if any code was changed, then re-run
   `/pr-selfcheck` and `gh pr checks --watch` to confirm the PR
   is still consistent and CI passes.

The code review is single-pass — do not re-run after fixes.
`/pr-selfcheck` runs again in Phase 3 to catch inconsistencies
introduced by review fix changes.

Never end a turn that claims ongoing waiting (delegated fix push,
CI run, CI rerun, external state change) without an armed event
source — a Monitor on the branch head, or `gh pr checks --watch`
with `run_in_background: true`. After every `gh run rerun` or other
re-kick, re-arm the watch before yielding. State what is being
awaited in the final message before going idle.

### Phase 4: Finalize PR for review readiness

Bring the PR into a state where a human reviewer can act on it. This
covers three things:

1. Reflect actual verification in the PR body. Update the body to
   describe what was confirmed, with evidence (HTTP status, Location
   header, Lambda runtime value, log excerpt, command output summary,
   etc.) so each claim is auditable later. If the body has checkbox
   items, sync `[ ]` to `[x]` as each item's condition is confirmed;
   if not, edit the Verification section text directly. Items still
   pending stay as `[ ]` (or noted explicitly as pending).
1. Confirm acceptance criteria are met. Cross-check the PR body and
   any linked issue against the actual change. If something is unmet,
   either address it or call it out as out-of-scope / follow-up.
1. Surface Phase 4 completion so the user can decide whether to mark
   the PR ready for review. `gh pr ready` is the user's call — do
   not run it unless explicitly instructed.

Update incrementally as conditions are confirmed (e.g., after Phase 1
CI passes, after apply / deploy succeeds, after post-deploy
verification with `curl`, `aws logs tail`, etc.).

Use the section 5 procedure (`gh pr edit --body-file`) for body
edits.

### Phase 5: Watch PR activity until merge

Arm the persistent `Monitor` running `pr-monitor <PR number>` in the
same turn you surface Phase 4 completion — before handing control back
to the user and before they flip the PR to ready. `READY_FOR_REVIEW`
is itself a monitored event, so an arm deferred until after the ready
flip can never observe it. It polls every 60s and emits one stdout line
per actionable change; quiet periods stay silent.

1. Event lines:
   - `STATE: MERGED` / `STATE: CLOSED` — top-level `state` changed.
   - `REVIEW: CHANGES_REQUESTED` / `REVIEW: APPROVED` —
     `reviewDecision` changed.
   - `READY_FOR_REVIEW` — `isDraft` flipped to false.
   - `NEW_COMMENT: [BOT|USER] <author> <path>:<line>` — new review-
     thread comment, thread `isResolved == false` and
     `isOutdated == false`. `[BOT|USER]` is a routing hint per
     `pr-reaction.md`; the rule's full thread walk still governs
     mutations.
   - `NEW_TOP_COMMENT: [BOT|USER] <author>` — new top-level PR
     comment.
   - `NEW_REVIEW: [BOT|USER] <author> <state>` — new PR review
     (summary body). `state` ∈ `COMMENTED` / `APPROVED` /
     `CHANGES_REQUESTED` / `DISMISSED`. Empty-body reviews filtered.
   - `CI_FAILURE: <check name>` — new `FAILURE` on the PR's head SHA.

1. Re-fetch detail on each event with:
   - `gh pr view <number> --json state,isDraft,reviewDecision,latestReviews,statusCheckRollup,comments,updatedAt,mergedAt,headRefName`
   - `gh pr-review review view -R <owner>/<repo> <number>` — add
     `--unresolved --not_outdated` for full-PR sweeps; drop them when
     inspecting a specific `NEW_COMMENT` that may have been resolved
     in the interim.
   - `gh run list --branch <headRefName> --json databaseId,name,status,conclusion,createdAt,headSha,workflowName --limit 20`

   The notification is not a user reply — keep working.

1. Before any push:
   - Verify the current branch matches the PR's `headRefName`.
   - `git fetch` and confirm local HEAD is still ahead of
     `origin/<branch>` (no manual push in between).
   - Skip the push if either check fails; surface the conflict to the
     user.

1. React per `pr-reaction.md` (bot check, reply-channel routing,
   thread resolve, cap for autonomous fix pushes).

1. `CI_FAILURE`: get the `databaseId` from `gh run list`, inspect with
   `gh run view --log-failed <databaseId>`, then fix and push (same
   pre-push checks).

1. Exit conditions:
   - `STATE: MERGED` → execute Step 6 (Cleanup), then `TaskStop` the
     monitor.
   - `STATE: CLOSED` without merge → `TaskStop`, skip cleanup.
   - Session ends → Monitor terminates with the session (best-effort).

1. Conflict handling:
   - Manual user push during monitor: acknowledge on the next event,
     keep watching. Do not revert or duplicate.
   - New user instruction superseding the watch: `TaskStop` the
     monitor, prioritize the user request.

`PushNotification` only for events that change what the user would do
next (merge, or "needs human attention" after the fix cap). Skip
routine CI / comment events.

## 5. Update a PR / issue (title / body)

- Update title:
  `gh pr edit <number> --title '...'`
- Update body (always use `--body-file`, never `--body`):
  1. Fetch the current body:
     `gh pr view <number> --json body --jq .body`
     (or `gh issue view <number> --json body --jq .body` for issues)
  1. Output a diff between the current body and the new body in the
     conversation (so what changed is visible and recoverable).
  1. Write the new body to a fresh file under the session scratchpad
     directory using the Write tool (new filename per revision — no
     temp-file generation, no Read of an empty file)
  1. Execute the edit:
     `gh pr edit <number> --body-file <body file path>`
     (or `gh issue edit <number> --body-file <body file path>`)
  The goal is observability — always show the diff so the user can see
  what changed and recover manually-written content if accidentally
  overwritten.

Note: Always use `--body-file` for any body update. The `#`-prefixed lines
in PR/issue bodies trigger Claude Code's security pre-check when passed
via `--body`, which cannot be bypassed by hooks.

## 6. Cleanup After Task Completion

After the PR is merged (or the task is fully done):

1. Move back to the repository root:
   `cd <repository root>`
1. Run `git cleanup` once.
