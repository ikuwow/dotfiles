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

Three-phase review: pass all mechanical checks first, then run
code reviews, then consolidate.

### Phase 1: PR self-review + CI (parallel)

Launch both at the same time:

- `/pr-selfcheck <PR number>` — PR presentation review.
- `gh pr checks --watch` — CI monitoring.

Wait for both to finish. If either fails:
- Fix self-review "Must Fix" / "Should Fix" items.
- Fix CI failures (`gh run view --log-failed`).
- Push fixes, then re-run both until both pass.

Note: `/pr-selfcheck` is a mechanical check, not a code review.
Re-running it after fixes is expected. The "single-pass" policy
applies only to code reviews in Phase 2.

### Phase 2: Code reviews (parallel)

Once Phase 1 passes, launch both:

- `/codex:adversarial-review` — challenges design decisions via Codex.
  Always run in the background (`run_in_background: true`) without
  asking the user for the execution mode. Do not use `AskUserQuestion`
  for foreground/background selection.
  After receiving the review output, immediately provide your own
  assessment of each finding (agree/disagree with reasoning) and
  propose concrete next actions. Never output the review verbatim
  and stop.
  If it fails with `disable-model-invocation` error, skip and continue
  with Phase 3. This is a known upstream issue
  (openai/codex-plugin-cc#211, anthropics/claude-code#43809) — once
  fixed, this command should work directly via the Skill tool.
- `/pr-review-toolkit:review-pr` — multi-agent code review (CLAUDE.md
  compliance, bug detection, error handling, test coverage).
  Reports findings in the conversation, does not post PR comments.

### Phase 3: Consolidate and fix

Once both reviews finish, review the combined results:

1. Fix issues found by code reviews.
2. Push fixes if any code was changed, then re-run
   `/pr-selfcheck` and `gh pr checks --watch` to confirm the PR
   is still consistent and CI passes.

Code reviews are single-pass — do not re-run after fixes.
`/pr-selfcheck` runs again in Phase 3 to catch inconsistencies
introduced by review fix changes.

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
