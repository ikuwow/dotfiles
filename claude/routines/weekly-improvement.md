# Weekly Dotfiles Improvement Routine

You are improving the ikuwow/dotfiles repository as a weekly maintenance routine.
This file contains all instructions for the routine.

## Step 1: Check Past Feedback

Before making any changes, check past routine PRs for feedback:

1. List past routine PRs:
   `gh pr list --repo ikuwow/dotfiles --search 'improve/dotfiles' --state all --limit 20`
2. For any closed (not merged) PRs, read the comments to understand why they were rejected:
   `gh pr view <number> --repo ikuwow/dotfiles --comments`
3. Learn from this feedback. Avoid making similar changes that were previously rejected.

## Step 2: Understand the Repository

1. Read `AGENTS.md` (or `CLAUDE.md`) to understand repository rules and conventions.
2. Read `README.md` for the overall structure.
3. Read `scripts/deploy.sh` to understand symlink mappings.
4. Explore the codebase to find improvement opportunities.

## Step 3: Find Improvements

Look for improvements across the entire dotfiles repository:

- Shell scripts: shellcheck compliance, readability, error handling (`set -eu`)
- Configuration files: outdated settings, consistency, organization
- Claude Code config (`claude/`): rules, skills, hooks, settings
- Security: exposed secrets, insecure defaults
- Dead code or unused configurations
- Documentation: only where genuinely missing or incorrect

Do NOT modify:
- `AIRULES.md` (global AI rules, maintained manually by the user)
- `CLAUDE.md` / `AGENTS.md` (only fix clear errors)

## Step 4: Create a PR

If worthwhile improvements are found:

1. Create a branch: `improve/dotfiles-YYYY-MM-DD` (use today's date)
2. Make changes and commit with clear messages following `claude/rules/git-workflow.md`
3. Push and create a draft PR following `claude/rules/git-workflow.md` and `claude/rules/pr-guidelines.md`
4. PR body must include:
   - What was improved and why
   - How to verify each change
   - Reference to any past feedback that influenced decisions

If no worthwhile improvements are found, do not create a PR. End the session.

## Guidelines

- Make only changes you are confident about. Skip uncertain improvements.
- Avoid breaking changes. Dotfiles are used daily — stability matters.
- Keep changes small and focused. One PR per run with related fixes grouped together.
- Follow all conventions in `AGENTS.md`.
- Do NOT run `/pr-selfcheck` or code reviews — the PR is a draft for human review.
