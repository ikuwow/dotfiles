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
- Never modify commits that have already been pushed.
- Implementation plans MUST cover the full workflow as a bullet-list
  checklist — from branch setup (Step 1, before implementation)
  through cleanup (Step 7) — not just the post-edit steps. The
  detailed procedures (mktemp usage, gh commands, polling commands,
  etc.) live in this file and are already in system context, so plans
  MUST NOT restate them and MUST NOT instruct you to re-Read this
  file. Recommended bullet form:
  - Step 1: branch creation (note worktree vs branch-only per project rules)
  - Step 2: commit
  - Step 3: push
  - Step 4: draft PR creation
  - Step 5: CI wait & review (Phases 1–5)
  - Step 7: cleanup after merge
  (Step 6 is a utility section; reference it only if the plan involves
  editing an existing PR/issue body.) Plans must still surface
  scope-specific deviations explicitly — e.g., "skip Step 7 because
  the branch is kept" or "stop after Step 4, this PR stays as draft".

## 1. Start Work

1. Pull the latest default branch:
   `git pull`
2. Create a worktree and branch:
   `git-worktree-create <branch-name>`
3. Follow the command shown in the script output to move into the worktree.
4. If the project rules explicitly prohibit worktrees, create a branch only:
   `git checkout -b <branch-name>`

Note: `.worktrees/` is covered by the global gitignore.

## 2. Commit

- Pass the message in single quotes. Fall back to a heredoc only when the
  message itself contains single quotes.
- Never use command substitution (`$()` or backticks) inside the command.
- Append a blank line and `Co-authored-by:` trailer:
  ```
  git commit -m 'Short summary

  Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>'
  ```

## 3. Push

- First push (set upstream):
  `git push -u origin HEAD`
- Subsequent pushes:
  `git push`
- `git push --force` / `git push -f` is absolutely prohibited.
  If a force push is needed, ask the user to do it.

## 4. Create a PR

1. Generate a unique temp file path:
   `mktemp --suffix=.md`
   Run this as a standalone Bash command (no command substitution).
   Read the output to obtain the generated path.
   Then call the Read tool on that path once — `mktemp` creates an empty
   file, and the Write tool requires the file be Read first if it exists.
   The Read returns a "shorter than offset" warning, which is expected;
   the subsequent Write succeeds.
2. Write the PR body to the generated path using the Write tool:
   `Write(<path from mktemp>)`
   - Follow the repository's PR template if one exists.
   - Follow the PR Body Checklist and Review Criteria.
3. Create the PR as a draft:
   `gh pr create --draft --body-file <path from mktemp>`
   - Never use `--body` for PR creation. The `#`-prefixed lines in the body
     trigger Claude Code's security pre-check, which cannot be bypassed by
     hooks. Always go through `--body-file`.
4. After creating the PR, display the PR URL to the user:
   `gh pr view --json url --jq '.url'`
5. Proceed to CI wait (step 5).

## 5. CI Wait & Review

Five phases: pass all mechanical checks, run the code review,
consolidate fixes, finalize the PR for review readiness, then watch
PR activity until merge.

### Phase 1: PR self-review + CI (parallel)

Launch both in a single assistant message so they execute concurrently:

- `/pr-selfcheck <PR number>` — PR presentation review.
- `gh pr checks --watch` — CI monitoring. Run with `run_in_background: true`.

If either fails:
- Fix self-review "Must Fix" / "Should Fix" items.
- Fix CI failures (`gh run view --log-failed`).
- Push fixes, then re-run both until both pass.

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

1. Fix issues found by the code review.
2. Push fixes if any code was changed, then re-run
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
2. Confirm acceptance criteria are met. Cross-check the PR body and
   any linked issue against the actual change. If something is unmet,
   either address it or call it out as out-of-scope / follow-up.
3. Mark the PR ready for review. Run `gh pr ready <number>` to take it
   out of draft. Skip if the user asked to keep it as draft.

Update incrementally as conditions are confirmed (e.g., after Phase 1
CI passes, after apply / deploy succeeds, after post-deploy
verification with `curl`, `aws logs tail`, etc.) — do not wait until
the very end to do all of it at once.

This step is not optional. Execute it autonomously instead of waiting
for the user to remind you. Use the section 6 procedure
(`gh pr edit --body-file`) for body edits.

### Phase 5: Watch PR activity until merge

After Phase 4 marks the PR ready for review, arm a persistent
`Monitor` to watch the PR until it is merged or closed. Reviewers
(human, Devin, Copilot) often act soon after ready, and CI may still
be running. The Monitor runs a background poll loop whose stdout
lines become notifications, so only an actionable change wakes you —
quiet periods stay silent (unlike a timer-based `/loop`, which wakes
on every tick regardless of change).

1. Arm a persistent Monitor (`persistent: true`) running a poll loop
   that re-runs the three polling commands below every 60s and emits
   exactly ONE stdout line per actionable change:
   - `STATE: MERGED` / `STATE: CLOSED` — top-level `state` changed.
   - `REVIEW: CHANGES_REQUESTED` / `REVIEW: APPROVED` —
     `reviewDecision` changed.
   - `NEW_COMMENT: <author> <path>:<line>` — a review-thread comment
     (GraphQL `reviewThreads` query) whose ID was not seen before, in
     a thread where `isResolved == false` and `isOutdated == false`.
     Top-level PR comments aren't gated by resolution state — read them
     from the `comments` field when you re-fetch detail.
   - `CI_FAILURE: <check name>` — a new `FAILURE` in
     `statusCheckRollup` or a new failed run from `gh run list`.

   Script requirements:
   - Dedup new comments against a `mktemp` seen-IDs file
     (`comm -13`); track the previous top-level state / reviewDecision
     in shell vars. Emit nothing on a no-op poll — this silence is the
     whole point of the switch.
   - Coverage (silence ≠ success): the emit set must cover CI failure
     and both terminal states, not just the happy path. Guard each
     `gh` call with `|| true` (or `continue`) so one failed poll does
     not kill the monitor; a failed or empty fetch must not be read as
     a state change (no spurious event).
   - Exit the loop (or `TaskStop` from the reaction turn) once `state`
     is `MERGED` or `CLOSED`.
   - 60s interval is fine for a remote API and within rate limits.
     There is no `ScheduleWakeup` prompt-cache concern here because
     the poll loop's own ticks run in the background shell and do not
     wake you (only an emitted line does).

   Polling commands (reused inside the Monitor script and again when
   you re-fetch detail on an event — top-level fields, threads, and
   run history each carry information the others lack):

   - PR top-level state:
     `gh pr view <number> --json state,reviewDecision,latestReviews,statusCheckRollup,comments,updatedAt,mergedAt,headRefName`
   - Review threads with `isResolved` / `isOutdated` (REST
     `/pulls/<num>/comments` does not expose resolution status, so
     use GraphQL):
     ```
     gh api graphql -f query='query($owner:String!,$repo:String!,$num:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$num){reviewThreads(first:100){nodes{isResolved isOutdated comments(first:100){nodes{id author{login} body createdAt path line}}}}}}}' -f owner=<owner> -f repo=<repo> -F num=<number>
     ```
   - Workflow run history on the PR branch (catches CI cycles
     `statusCheckRollup` doesn't show — e.g. older runs, re-run jobs):
     `gh run list --branch <headRefName> --json databaseId,name,status,conclusion,createdAt,headSha,workflowName --limit 20`

2. On each event notification, re-fetch full detail with the three
   polling commands in step 1 (the event line is only a signal), then
   handle it per steps 4-6. The notification is not a user reply —
   keep working.

3. Before any push (any reaction that would write to origin):
   - Verify the current branch matches the PR's `headRefName`.
   - `git fetch` and confirm local HEAD is still ahead of
     `origin/<branch>` (no manual user push has happened in between).
   - Skip the push if either check fails; surface the conflict to the
     user instead of trying to reconcile silently.

4. React to the event:
   - `REVIEW: CHANGES_REQUESTED`, or a `NEW_COMMENT` in a thread where
     `isResolved == false` and `isOutdated == false` that is clearly a
     fix request (human, Devin, Copilot, etc.): read the content,
     modify code, push the fix. When the intent is ambiguous
     (question, nit, discussion), reply via `gh pr comment` instead of
     pushing code. Threads with `isResolved == true` or
     `isOutdated == true` are already addressed or no longer
     applicable — skip them.
   - `REVIEW: APPROVED` (no further action requested): report to the
     user in the next turn, do not act.
   - `CI_FAILURE`: get the `databaseId` from `gh run list` at re-fetch
     (`statusCheckRollup` check names don't always map 1:1 to run
     names), inspect with `gh run view --log-failed <databaseId>`, fix,
     push.
   - CI still in progress (`PENDING` / `IN_PROGRESS` / `QUEUED` seen
     when you re-fetch): no action, the Monitor will emit again when
     it resolves.

5. Cap for autonomous fix pushes:
   - Stop pushing autonomous fixes after 3 fix commits for this PR in
     this session. Beyond that, switch to reply-only mode and notify
     the user that the PR appears to need human attention. This
     prevents runaway loops when an automated reviewer keeps
     re-requesting changes on each push.

6. Exit conditions:
   - `STATE: MERGED` → execute Step 7 (Cleanup), then `TaskStop` the
     monitor.
   - `STATE: CLOSED` without merge → `TaskStop` the monitor, skip
     cleanup (user may reopen).
   - Session ends (PC sleep, Claude Code closed) → the Monitor
     terminates with the session. This is accepted as best-effort.

7. Conflict handling:
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
  2. Output a diff between the current body and the new body in the
     conversation (so what changed is visible and recoverable).
  3. Generate a unique temp file path:
     `mktemp --suffix=.md`
     Run this as a standalone Bash command and read the output.
     Then call the Read tool on that path once — `mktemp` creates an
     empty file, and the Write tool requires the file be Read first if
     it exists.
  4. Write the new body to the generated path:
     `Write(<path from mktemp>)`
  5. Execute the edit:
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
2. Remove the worktree (worktree-based workflows only):
   `git worktree remove .worktrees/<branch>`
   - Skip if the project prohibits worktrees and the branch was created
     via `git checkout -b` only.
3. Delete the merged local branch:
   `git delete-squashed`
   - Removes local branches whose content is already in the default
     branch, including squash-merged ones that `git branch -d` refuses
     ("not fully merged"). Unmerged branches are left untouched, and the
     script aborts on a dirty working tree.
   - Use the space form (`git delete-squashed`); it is already covered by
     the `Bash(git *)` allow rule, so no extra permission is needed.
