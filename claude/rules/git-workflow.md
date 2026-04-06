# Git Workflow

Standard git/GitHub workflow for all projects.
Follow each step in order. Skip steps that don't apply.

## Principles

- Never create or edit files on the default branch. Always move into the
  worktree (or feature branch) first. Creating files before branching
  leads to redundant copy-and-delete work.

## 1. Start Work

1. Pull the latest default branch:
   `git pull`
2. Create a worktree and branch:
   `git-worktree-create <branch-name>`
3. Move into the worktree directory using the relative path from the output:
   `cd .worktrees/<dir>`
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

1. Write the PR body to a temp file using the Write tool:
   `Write(/tmp/pr-body-<unique-id>.md)`
   Use a unique ID (e.g., branch name or timestamp) to avoid collisions
   with other parallel sessions.
   - Follow the repository's PR template if one exists.
   - Follow the PR Body Checklist in `pr-guidelines.md`.
2. Create the PR as a draft:
   `gh pr create --draft --body-file /tmp/pr-body-<unique-id>.md`
   - Never use `--body` for PR creation. The `#`-prefixed lines in the body
     trigger Claude Code's security pre-check, which cannot be bypassed by
     hooks. Always go through `--body-file`.
3. After creating the PR, display the PR URL to the user:
   `gh pr view --json url --jq '.url'`
4. Proceed to CI wait (step 5).

## 5. CI Wait & Self-Review

After pushing and creating/updating a PR, run CI monitoring and
self-review in parallel:

1. Start both at the same time:
   - Run `gh pr checks --watch` to monitor CI.
   - Launch a background subagent with `/pr-selfcheck <PR number>` to
     self-review the PR.
2. Once both finish, read the self-review output.
3. If the verdict is NEEDS_IMPROVEMENT:
   - Immediately fix all "Must Fix" items without waiting for user input.
   - Address "Should Fix" items where reasonable.
   - Update the PR (title, body, or code) as needed.
   - Push changes if code was modified, then re-run `gh pr checks --watch`.
4. If any CI check fails:
   - Review details: `gh pr checks`
   - View failure logs: `gh run view --log-failed`
   - Fix the issue, commit, push, then watch again.
5. Do not re-run the self-review after fixes (single pass only).

## 6. Mark PR as Ready for Review

Before marking the PR ready, run a self-review gate:

1. Run `/pr-selfcheck <PR number>`.
2. If the verdict is NEEDS_IMPROVEMENT:
   - Fix all "Must Fix" items. Address "Should Fix" items where reasonable.
   - Push changes, then re-run `gh pr checks --watch`.
   - Re-run `/pr-selfcheck` after fixes.
3. Once the verdict is PASS, mark the PR as ready:
   `gh pr ready`

## 7. Update a PR / issue (title / body)

- Update title:
  `gh pr edit <number> --title '...'`
- Update body (always use `--body-file`, never `--body`):
  1. Fetch the current body:
     `gh pr view <number> --json body --jq .body`
     (or `gh issue view <number> --json body --jq .body` for issues)
  2. Output a diff between the current body and the new body in the
     conversation (so what changed is visible and recoverable).
  3. Write the new body to a temp file:
     `Write(/tmp/pr-body-<unique-id>.md)`
  4. Execute the edit:
     `gh pr edit <number> --body-file /tmp/pr-body-<unique-id>.md`
     (or `gh issue edit <number> --body-file /tmp/pr-body-<unique-id>.md`)
  The goal is observability — always show the diff so the user can see
  what changed and recover manually-written content if accidentally
  overwritten.

Note: Always use `--body-file` for any body update. The `#`-prefixed lines
in PR/issue bodies trigger Claude Code's security pre-check when passed
via `--body`, which cannot be bypassed by hooks.

## 8. Cleanup After Task Completion

After the PR is merged (or the task is fully done):

1. Move back to the repository root:
   `cd <repository root>`
2. Remove the worktree:
   `git worktree remove .worktrees/<branch>`
