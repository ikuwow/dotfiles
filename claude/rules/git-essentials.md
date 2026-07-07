# Git Essentials

Core git/GitHub rules for all projects.

Every plan produced by EnterPlanMode's Phase 4 (Final Plan) MUST
include the workflow checklist below as an explicit section, from
branch setup through cleanup — regardless of whether the task looks
like "just docs" or otherwise low-ceremony. State scope-specific
deviations explicitly (e.g., "stop after Step 3, skip CI wait").
Omitting the checklist section from a Plan Mode plan is never
correct. (Truly trivial fixes that don't warrant Plan Mode at all
are a separate judgment call — see EnterPlanMode's own criteria.)

The full procedure (worktree setup, PR body rules, CI phases,
monitoring, cleanup) lives in the git-workflow skill, which Claude
loads automatically based on its own description when the task
matches — this rule does not control that; it only names where the
detail lives. Plans MUST NOT restate the detailed procedures from
the skill. If the skill doesn't trigger on its own, invoke it
explicitly (`Skill(git-workflow)` or `/git-workflow`) rather than
improvising the flow from this checklist alone.

## Workflow checklist

- Step 1: pull default branch, create branch
  (`git-worktree-create <branch>`, or `git checkout -b` where
  project rules prohibit worktrees)
- Step 2: implement, commit, push
- Step 3: create a draft PR (`gh pr create --draft --body-file`)
- Step 4: CI wait and review (Phases 1-5)
- Step 6: cleanup after merge (`git cleanup-branches`)

## Branch

- Claude Code's `--worktree` flag and the EnterWorktree tool must
  never be used (known bugs)
- Never create or edit files on the default branch — branch first

## Commit

- Append a blank line and a
  `Co-authored-by: Claude <model name> <noreply@anthropic.com>`
  trailer, naming the model actually in use. When the harness
  prescribes its own trailer format, that format wins.
- Emit exactly one Claude trailer block per commit. When project
  rules prescribe a different Co-authored-by string, the winning
  format replaces it — do not stack both.
- Never modify commits that have already been pushed

## Push

- First push: `git push -u origin HEAD`; afterwards `git push`
- Force push variants (`--force`, `-f`, `--force-with-lease`) are
  absolutely prohibited unless the user explicitly instructs
  otherwise. If a chosen path would require one, or `git reset
  --hard` on a published branch, back out to a merge-based path:
  `gh pr update-branch <N>`, merge the default branch into the
  feature branch, or a fresh commit on top.
