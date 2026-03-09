# Git Workflow

Standard git/GitHub workflow for all projects.
Follow each step in order. Skip steps that don't apply.

## 1. Start Work

1. Pull the latest default branch:
   `git pull`
2. Create a worktree and branch:
   `git-worktree-create <branch-name>`
3. Move into the worktree directory:
   `cd <output directory>`
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
   - Describe only what was actually verified under "confirmed" items.
2. Create the PR as a draft:
   `gh pr create --draft --body-file /tmp/pr-body-<unique-id>.md`
   - Never use `--body` for PR creation. The `#`-prefixed lines in the body
     trigger Claude Code's security pre-check, which cannot be bypassed by
     hooks. Always go through `--body-file`.
3. After creating the PR, proceed to CI wait (step 5).

## 5. CI Wait

After pushing and creating/updating a PR, wait for CI:

1. Watch all checks:
   `gh pr checks --watch`
2. If any check fails:
   - Review details: `gh pr checks`
   - View failure logs: `gh run view --log-failed`
   - Fix the issue, commit, push, then watch again.

## 6. Update a PR (title / body)

- Update title:
  `gh pr edit <number> --title '...'`
- Update body:
  `gh pr edit <number> --body '...'`
  Use `--body` (not `--body-file`) so the content is visible in the
  permission dialog. Fall back to `--body-file` only when the body contains
  `#`-prefixed lines after a newline.
- Always fetch the latest PR content before editing remote content.

## 7. Cleanup After Task Completion

After the PR is merged (or the task is fully done):

1. Move back to the repository root:
   `cd <repository root>`
2. Remove the worktree:
   `git worktree remove .worktrees/<branch>`
