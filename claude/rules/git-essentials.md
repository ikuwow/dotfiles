# Git Essentials

Always-on git rules — apply to every code-touching turn. For
task-onset operations (branch creation, PR creation, CI watch, PR /
issue body edits, cleanup), see `claude/rules/git-workflow.md`. For
PR body authoring or self-review, see `claude/rules/pr-guidelines.md`.

## Commit

- Pass the message in single quotes. Fall back to a heredoc only
  when the message itself contains single quotes.
- Never use command substitution (`$()` or backticks) inside the
  command.
- Append a blank line and `Co-authored-by:` trailer:
  ```
  git commit -m 'Short summary

  Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>'
  ```

## Push

- First push (set upstream): `git push -u origin HEAD`
- Subsequent pushes: `git push`
- `git push --force` / `git push -f` is absolutely prohibited. If a
  force push is needed, ask the user to do it.
