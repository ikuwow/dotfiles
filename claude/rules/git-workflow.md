# Git Workflow

Standard git/GitHub workflow for all projects.
Follow each step in order. Skip steps that don't apply.

Prerequisite: the `agynio/gh-pr-review` gh extension is installed
(used by Phase 5 review-thread reactions).

## Principles

- All steps within a single workflow run are pre-authorized by the user
  who initiated the task. Do not pause between steps to ask for
  confirmation unless blocked by an error or ambiguity. Execute the
  full flow continuously and report results at the end.
- Never create or edit files on the default branch. Always move into the
  worktree (or feature branch) first. Creating files before branching
  leads to redundant copy-and-delete work.
- Never modify commits that have already been pushed
- Implementation plans MUST cover the full workflow as a bullet-list
  checklist — from branch setup (Step 1, before implementation)
  through cleanup (Step 7) — not just the post-edit steps. The
  detailed procedures (mktemp usage, gh commands, polling commands,
  etc.) live in this file and are already in system context, so plans
  MUST NOT restate them and MUST NOT instruct you to re-Read this
  file. Recommended bullet form:
  - Step 1: branch creation (note worktree vs branch-only per project rules)
  - Step 2: implement, commit, push
  - Step 4: draft PR creation
  - Step 5: CI wait & review (Phases 1–5)
  - Step 7: cleanup after merge
  (Step 6 is a utility section; reference it only if the plan involves
  editing an existing PR/issue body.) Plans must still surface
  scope-specific deviations explicitly — e.g., "skip Step 7 because
  the branch is kept" or "stop after Step 4, skip CI wait & review".

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

## 4. Create a PR

1. Generate a unique temp file path:
   `mktemp --suffix=.md`
   Run this as a standalone Bash command (no command substitution).
   Read the output to obtain the generated path.
   Then call the Read tool on that path once — `mktemp` creates an empty
   file, and the Write tool requires the file be Read first if it exists.
   The Read returns a "shorter than offset" warning, which is expected;
   the subsequent Write succeeds.
1. Write the PR body to the generated path using the Write tool:
   `Write(<path from mktemp>)`
   - Follow the repository's PR template if one exists
   - Follow the PR Body Checklist
1. Create the PR as a draft:
   `gh pr create --draft --body-file <path from mktemp>`
   - Never use `--body` for PR creation. The `#`-prefixed lines in the body
     trigger Claude Code's security pre-check, which cannot be bypassed by
     hooks. Always go through `--body-file`.
1. After creating the PR, display the PR URL to the user:
   `gh pr view --json url --jq '.url'`
1. Proceed to CI wait (step 5)

## 5. CI Wait & Review

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
verification with `curl`, `aws logs tail`, etc.) — do not wait until
the very end to do all of it at once.

This step is not optional. Execute it autonomously instead of waiting
for the user to remind you. Use the section 6 procedure
(`gh pr edit --body-file`) for body edits.

### Phase 5: Watch PR activity until merge

After Phase 4 completes, arm a persistent `Monitor` running
`pr-monitor <PR number>`. It polls every 60s and emits one stdout line
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
   - `STATE: MERGED` → execute Step 7 (Cleanup), then `TaskStop` the
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

## 6. Update a PR / issue (title / body)

- Update title:
  `gh pr edit <number> --title '...'`
- Update body (always use `--body-file`, never `--body`):
  1. Fetch the current body:
     `gh pr view <number> --json body --jq .body`
     (or `gh issue view <number> --json body --jq .body` for issues)
  1. Output a diff between the current body and the new body in the
     conversation (so what changed is visible and recoverable).
  1. Generate a unique temp file path:
     `mktemp --suffix=.md`
     Run this as a standalone Bash command and read the output.
     Then call the Read tool on that path once — `mktemp` creates an
     empty file, and the Write tool requires the file be Read first if
     it exists.
  1. Write the new body to the generated path:
     `Write(<path from mktemp>)`
  1. Execute the edit:
     `gh pr edit <number> --body-file <path from mktemp>`
     (or `gh issue edit <number> --body-file <path from mktemp>`)
  The goal is observability — always show the diff so the user can see
  what changed and recover manually-written content if accidentally
  overwritten.

Note: Always use `--body-file` for any body update. The `#`-prefixed lines
in PR/issue bodies trigger Claude Code's security pre-check when passed
via `--body`, which cannot be bypassed by hooks.

## 7. Cleanup After Task Completion

After the PR is merged (or the task is fully done):

1. Move back to the repository root:
   `cd <repository root>`
1. Delete unused local branches (merged, squash-merged, or upstream
   gone) along with their worktrees, and prune stale worktree entries:
   `git cleanup-branches`
   - Use the space form (`git cleanup-branches`); it is already covered
     by the `Bash(git *)` allow rule, so no extra permission is needed.
   - Plain `git branch -d` rejects squash-merged branches as "not fully
     merged", so a custom sweep is needed for repos that squash on
     merge.
