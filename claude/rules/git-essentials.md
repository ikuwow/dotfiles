# Git Essentials

Always-on git rules. Task-onset workflow (branch creation, PR
creation, CI watch, PR / issue body edits, cleanup) lives in
`git-workflow.md`. PR body authoring and self-review style lives in
`pr-guidelines.md`.

Shell quoting discipline (single quotes, no `$()` / backticks,
heredoc fallback for embedded single quotes) is governed by the
general shell rules in `AIRULES.md` and applies to git commands too.

## Branch

- Claude Code's `--worktree` flag and the EnterWorktree tool must
  never be used (known bugs). Start work with `git checkout -b`
  unless the project's own rules prescribe a different tool such
  as `git-worktree-create`.

## Commit

Append a blank line and `Co-authored-by:` trailer:

```
git commit -m 'Short summary

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>'
```

## Push

- First push (set upstream): `git push -u origin HEAD`
- Subsequent pushes: `git push`
- `git push --force` / `git push -f` is absolutely prohibited. If a
  force push is needed, ask the user to do it.
