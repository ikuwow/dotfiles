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
- Implementation plans MUST include the full workflow from Step 1
  through Step 5. Never produce a plan that ends at "edit the file"
  without covering commit, push, PR creation, and CI review.

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

After Phase 4 marks the PR ready for review, start a `/loop` to watch
the PR until it is merged or closed. Reviewers (human, Devin, Copilot)
often act soon after ready, and CI may still be running — the watch
loop catches activity and reacts autonomously instead of waiting for
the user to re-engage.

1. Start the watch loop in dynamic mode (no interval — let Claude
   self-pace via `ScheduleWakeup`):

   ```
   /loop Watch PR #<number>: poll `gh pr view <number> --json state,reviewDecision,latestReviews,statusCheckRollup,comments,updatedAt,mergedAt`. On new activity, react per the rules in git-workflow.md Phase 5. Exit when state becomes MERGED or CLOSED.
   ```

2. Each iteration, check for new activity and act:
   - **Review with `CHANGES_REQUESTED`** or new inline review comment
     (human, Devin, Copilot, etc.): read the content, modify code,
     push the fix. Reply via `gh pr comment` only when the comment is
     a question rather than a fix request.
   - **Review with `APPROVED`** (no further action requested): report
     to the user in the next assistant turn, do not act.
   - **CI failure** (`statusCheckRollup` contains FAILURE): inspect
     with `gh run view --log-failed`, fix, push.
   - **CI in progress** (`PENDING` / `IN_PROGRESS`): no action, wait.
   - **No change since last check**: no action.

3. Pacing guidance for `ScheduleWakeup`:
   - Recent activity (within last hour): 2–3 minute interval (120–180s).
   - Quiet: 20–30 minute interval (1200–1800s).
   - Tool clamps to [60, 3600]s.

4. Exit conditions:
   - `state` becomes `MERGED` → execute Step 7 (Cleanup) inside the
     same loop iteration, then end the loop.
   - `state` becomes `CLOSED` without merge → end the loop, skip
     cleanup (user may reopen).
   - Session ends (PC sleep, Claude Code closed) → loop terminates
     silently. This is accepted as best-effort.

5. Conflict handling:
   - If the user pushes commits manually while the loop is running,
     just acknowledge in the next iteration and continue watching.
     Do not try to revert or duplicate the user's work.
   - If the user gives a new instruction that supersedes the watch,
     pause / cancel the loop and prioritize the user request.

This step is the final stage of the workflow. It is best-effort by
design — for event-driven reliability use GitHub Actions instead.

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
2. Remove the worktree:
   `git worktree remove .worktrees/<branch>`
