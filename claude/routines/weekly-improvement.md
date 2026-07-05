# Weekly Dotfiles Improvement Routine

You are improving the ikuwow/dotfiles repository as a weekly maintenance routine.
This file contains all instructions for the routine.

## Step 1: Check Past Feedback and Retrospectives

Before making any changes, check past routine PRs for feedback:

1. List past routine PRs:
   `gh pr list --repo ikuwow/dotfiles --label 'claude-routine' --state all --limit 20 --json number,title,state,mergedAt`
1. For any closed (not merged) PRs, read the comments to understand why they were rejected:
   `gh pr view <number> --repo ikuwow/dotfiles --comments`
1. Learn from this feedback. Avoid making similar changes that were previously rejected

Then pull the retrospective backlog:

1. List open retrospective issues:
   `gh issue list --repo ikuwow/dotfiles --label retrospective --state open --json number,title,body`
1. Treat their countermeasures as the primary improvement candidates for this run. Look for patterns across multiple issues (the same rule failing repeatedly, accumulating rule bloat) before implementing any single countermeasure verbatim.
1. After a countermeasure is implemented (or rejected with reason), close the issue with a comment linking the PR or stating the decision.

## Step 2: Understand the Repository

Read `AGENTS.md` to understand repository rules, conventions, and structure.
Then explore the codebase to find improvement opportunities.

## Step 3: Find Improvements

Look for improvements across the entire dotfiles repository:

- Shell scripts: shellcheck compliance, readability, error handling (`set -eu`)
- Configuration files: outdated settings, consistency, organization
- Claude Code config (`claude/`): rules, skills, hooks, settings
- Security: exposed secrets, insecure defaults
- Dead code or unused configurations
- Documentation: only where genuinely missing or incorrect
- Rule budget: always-loaded rule files stay within budget (`AIRULES.md` <= 140 lines, each `claude/rules/*.md` <= 100 lines). Propose consolidation or tier demotion when exceeded

Modify with care:
- `AIRULES.md`: only when implementing a countermeasure recorded in a retrospective issue, or bringing it back within the rule budget above; cite the issue or the budget overage in the PR body
- `CLAUDE.md` / `AGENTS.md` (only fix clear errors)

## Step 4: Create a PR

If worthwhile improvements are found:

1. Ensure the `claude-routine` label exists:
   `gh label create 'claude-routine' --repo ikuwow/dotfiles --description 'Created by Claude Code weekly routine' --color '6e40c9' --force`
1. Create a branch: `improve/dotfiles-YYYY-MM-DD` (use today's date)
1. Make changes and commit with clear messages
1. Follow the git-workflow skill's Steps 1-3 only (push + create draft PR with `--label 'claude-routine'`)
   Skip Step 4 entirely (CI wait, self-review, and code reviews) — this is a draft for human review.
1. Follow `claude/skills/git-workflow/pr-guidelines.md` for the PR body. It must include:
   - What was improved and why
   - How to verify each change
   - Reference to any past feedback that influenced decisions

If no worthwhile improvements are found, do not create a PR. End the session.

## Guidelines

- Make only changes you are confident about. Skip uncertain improvements
- Avoid breaking changes. Dotfiles are used daily — stability matters
- Keep changes small and focused. One PR per run with related fixes grouped together
- Follow all conventions in `AGENTS.md`
