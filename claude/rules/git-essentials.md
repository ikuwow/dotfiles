# Git Essentials

Every plan produced by EnterPlanMode's Phase 4 (Final Plan) MUST
list the steps of the git-workflow skill as an explicit section, from
branch setup through cleanup. State scope-specific deviations
explicitly (e.g., "stop after creating the draft PR, skip CI wait").

Invoke `Skill(git-workflow)` (or `/git-workflow`) to read those steps
and before creating a branch, since the full procedure lives there.
Plans MUST NOT restate the detailed procedures from the skill.

## Commit

- Append a blank line and exactly one Claude trailer block:
  `Co-authored-by: Claude <model name> <noreply@anthropic.com>`,
  naming the model actually in use. When the harness or project
  rules prescribe a different trailer format, that format replaces
  this one (harness wins over project rules) — never stack a second
  trailer block.

## Push

- First push: `git push -u origin HEAD`; afterwards `git push`
- When a path would need a force push, or `git reset --hard` on a
  published branch, back out to a merge-based one: `gh pr
  update-branch <N>`, merge the default branch into the feature
  branch, or a fresh commit on top.
