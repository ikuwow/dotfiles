# Git Essentials

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
- Force push variants (`--force`, `-f`, `--force-with-lease`) are
  prohibited. If the chosen path would need one of them, or a
  `git reset --hard` on a published branch, back out to a non-force
  alternative — `gh pr update-branch <N>`, `git merge main` into the
  feature branch, or a fresh commit on top. Do not escalate to asking
  the user; find the merge-based path.
