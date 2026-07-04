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
  absolutely prohibited unless the user explicitly instructs otherwise.
  This is a path-selection rule, not a safety verdict on
  `--force-with-lease` in general (which is safer than `--force`); the
  point is that a chosen work path shouldn't require rewriting
  published history. If the path would need any force variant or a
  `git reset --hard` on a published branch, back out to a non-force
  alternative — `gh pr update-branch <N>`, `git merge main` into the
  feature branch, or a fresh commit on top. Do not auto-escalate to
  asking the user to force-push; find the merge-based path.
