# Git Workflow

Standard git/GitHub workflow for all projects.
Follow each step in order. Skip steps that don't apply.

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

After Phase 4 completes, arm a persistent `Monitor` to watch the PR
until it is merged or closed. Reviewers (human, Devin, Copilot) often
act soon after the user marks the PR ready, and CI may still be
running. The Monitor runs a background poll loop whose stdout
lines become notifications, so only an actionable change wakes you —
quiet periods stay silent (unlike a timer-based `/loop`, which wakes
on every tick regardless of change).

1. Arm a persistent Monitor (`persistent: true`) running
   `pr-monitor <PR number>`. The script polls every 60s and emits
   exactly ONE stdout line per actionable change. Event lines:
   - `STATE: MERGED` / `STATE: CLOSED` — top-level `state` changed
   - `REVIEW: CHANGES_REQUESTED` / `REVIEW: APPROVED` —
     `reviewDecision` changed.
   - `READY_FOR_REVIEW` — `isDraft` changed from true to false (the
     user marked the PR ready).
   - `NEW_COMMENT: <author> <path>:<line>` — a review-thread comment
     whose ID was not seen before, in a thread where `isResolved ==
     false` and `isOutdated == false`.
   - `NEW_TOP_COMMENT: <author>` — a top-level PR comment whose ID
     was not seen before. Not gated by resolution state.
   - `NEW_REVIEW: <author> <state>` — a PR review (summary body) whose
     ID was not seen before. `state` is `COMMENTED` / `APPROVED` /
     `CHANGES_REQUESTED` / `DISMISSED`. Catches reviews that do not
     change `reviewDecision` (e.g. Devin Review posted as `COMMENTED`,
     or a human submitting "Comment"). Empty-body reviews are filtered
     out.
   - `CI_FAILURE: <check name>` — a new `FAILURE` from `gh run list`
     on the PR's head SHA.

   Quiet periods stay silent. The script exits on its own when the PR
   reaches MERGED or CLOSED; otherwise stop it with `TaskStop` from a
   reaction turn.

   When you re-fetch detail on an event (the line itself is only a
   signal), the polling commands the script uses are:

   - PR top-level state:
     `gh pr view <number> --json state,isDraft,reviewDecision,latestReviews,statusCheckRollup,comments,updatedAt,mergedAt,headRefName`
   - Review threads (state + bodies + path/line) and PR reviews (state
     + summary body) in one call — the `agynio/gh-pr-review` extension
     assembles reviews, inline comments, and thread replies into a
     single JSON payload so no separate GraphQL / REST calls are
     needed:
     `gh pr-review review view -R <owner>/<repo> <number> --include-comment-node-id`
     Add `--unresolved --not_outdated` to trim already-handled threads.
     Drop those flags when a `NEW_COMMENT` may have been resolved in
     the interim and you need to see it anyway.
   - Workflow run history on the PR branch (catches CI cycles
     `statusCheckRollup` doesn't show — e.g. older runs, re-run jobs):
     `gh run list --branch <headRefName> --json databaseId,name,status,conclusion,createdAt,headSha,workflowName --limit 20`

1. On each event notification, re-fetch full detail with the three
   polling commands in step 1 (the event line is only a signal), then
   handle it per steps 3-7 below. The notification is not a user
   reply — keep working.

1. Before any push (any reaction that would write to origin):
   - Verify the current branch matches the PR's `headRefName`
   - `git fetch` and confirm local HEAD is still ahead of
     `origin/<branch>` (no manual user push has happened in between).
   - Skip the push if either check fails; surface the conflict to the
     user instead of trying to reconcile silently.

1. React by content, not event type. `NEW_COMMENT` is pre-filtered by
   the monitor to unresolved, non-outdated threads; `NEW_TOP_COMMENT`
   is not, so classify it by content:
   - Clear fix request (`CHANGES_REQUESTED`, a `NEW_COMMENT`, a
     `NEW_TOP_COMMENT`, or a `NEW_REVIEW` asking for a change — from a
     human or an automated reviewer like Devin or Copilot): modify code
     and push, subject to the step-3 pre-push checks and the step-5 cap.
     For a `NEW_COMMENT`, if the re-fetched thread is now `isResolved`
     or `isOutdated`, it was handled in the interim — skip it. For a
     `NEW_REVIEW`, re-fetch the review body to classify intent.
   - Question, nit, or ambiguous intent: reply and do not push. Pick
     the reply channel by event type so context stays intact:
     - `NEW_COMMENT` (review thread comment): reply inside the thread
       with `gh pr-review comments reply --thread-id <id> --body <text> -R <owner>/<repo> <number>`.
     - `NEW_TOP_COMMENT` / `NEW_REVIEW`: no thread to attach to; post
       a top-level PR comment with `gh pr comment <number> --body <text>`.
   - `READY_FOR_REVIEW`: the user took the PR out of draft; no action,
     just register that review activity is now expected.
   - Informational (`APPROVED`, or CI still `PENDING` / `IN_PROGRESS` /
     `QUEUED`): no action; surface it to the user on the next turn.

   Resolving review threads (`NEW_COMMENT` only — top-level comments
   and review summary bodies are not threads):
   - After a fix push that addresses a `NEW_COMMENT`, resolve the
     originating thread so subsequent monitor passes skip it and
     reviewers see the discussion state.
   - After a reply that closes a question / nit / ambiguous-intent
     comment (e.g., explaining an intentional decision), resolve the
     thread.
   - Leave the thread open when waiting for the reviewer's follow-up.
   - Get the thread id from the `review view` output in step 1
     (`thread_id` field), then run
     `gh pr-review threads resolve --thread-id <thread-id> -R <owner>/<repo> <number>`.

   Event-specific notes:
   - `STATE: MERGED` / `CLOSED` is terminal — handled in step 6 (Exit
     conditions), not here.
   - `NEW_TOP_COMMENT` carries only the author; re-fetch the body from
     the `comments` field before classifying.
   - `CI_FAILURE`: get the `databaseId` from `gh run list` (check names
     don't always map 1:1 to run names), inspect with
     `gh run view --log-failed <databaseId>`, then fix and push.

1. Cap for autonomous fix pushes:
   - Stop pushing autonomous fixes after 3 fix commits for this PR in
     this session. Beyond that, switch to reply-only mode and notify
     the user that the PR appears to need human attention. This
     prevents runaway loops when an automated reviewer keeps
     re-requesting changes on each push.

1. Exit conditions:
   - `STATE: MERGED` → execute Step 7 (Cleanup), then `TaskStop` the
     monitor.
   - `STATE: CLOSED` without merge → `TaskStop` the monitor, skip
     cleanup (user may reopen).
   - Session ends (PC sleep, Claude Code closed) → the Monitor
     terminates with the session. This is accepted as best-effort.

1. Conflict handling:
   - If the user pushes commits manually while the Monitor is running,
     just acknowledge on the next event and continue watching. Do not
     try to revert or duplicate the user's work.
   - If the user gives a new instruction that supersedes the watch,
     `TaskStop` the monitor and prioritize the user request.

Notifications follow the Monitor tool's default guidance: an event
landing in chat (and the existing `noti` Notification hook firing when
you wake) is enough; reserve any explicit `PushNotification` for events
that change what the user would do next (e.g. merge, or "needs human
attention" after the fix cap). Do not push on routine CI / comment
events.

This is the final phase of Step 5; Step 7 (Cleanup) still runs when the
Monitor exits on `MERGED`. The watch is best-effort by design — for
event-driven reliability use GitHub Actions instead.

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
