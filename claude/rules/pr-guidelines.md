# PR Guidelines

Quality criteria for pull requests. Referenced by both the PR creation
step in `git-workflow.md` and the `/pr-selfcheck` skill.

## Writing Style

- Summarize the change at a high level. Do not mirror the diff line-by-line.
- Keep bullet points few and meaningful. Each bullet should convey a
  distinct decision or outcome, not an individual code change.
- Anything a reviewer can see by reading the diff does not need to be
  restated in the body. Focus on context the diff cannot convey: why the
  change was made, trade-offs considered, and things to watch out for.

## PR Body Checklist

When writing a PR body, cover every applicable item:

1. Purpose and motivation
   - State what changed and why (bug, feature, tech debt, compliance, etc.).
   - A reviewer should understand the intent from the body alone.

2. Scope
   - Clearly describe the boundary of the change.
   - Call out anything intentionally left out of scope.

3. Sources and references
   - Provide official documentation URLs or other authoritative sources
     that justify configuration values, tool choices, or version selections.
   - Especially important for dotfiles / infrastructure changes where
     "why this value" matters.

4. Verification
   - Describe only what was actually verified under "confirmed" items.
   - Do not claim verification that was not performed.

## Review Criteria

Used by `/pr-selfcheck` to evaluate a PR after creation.

1. Reviewer-facing information
   - Can a reviewer understand the purpose, what changed, and the impact
     from the PR body alone?
   - Is the scope of the change clear?

2. Sources and references
   - Are official documentation URLs or other authoritative sources provided
     to justify configuration values, tool choices, or version selections?

3. Intent and rationale
   - Does the PR explain not just what changed but why?
   - Is the motivation stated?

4. Link validity
   - Do all URLs in the PR body resolve to the expected content?
   - Do anchor links point to the correct section?

5. Title / body / diff consistency
   - Does the PR title accurately reflect the change?
   - Is there any contradiction between the body description and the
     actual diff?

6. Diff coverage
   - Does the PR body account for all files and changes in the diff?
   - Are there unexplained changes?

7. Conciseness
   - Is the body a high-level summary rather than a line-by-line restatement
     of the diff?
   - Are bullet points few and meaningful, each conveying a distinct point?
