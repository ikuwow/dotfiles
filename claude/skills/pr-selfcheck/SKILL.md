---
description: Perform a self-review of a PR before requesting human review. TRIGGER when user invokes /pr-selfcheck, or when the git workflow reaches the self-review step after PR creation. Accepts a PR number as an argument.
---

# PR Self-Check

Perform a self-review of the specified PR to catch issues before a human reviewer sees it.

## Steps

1. Retrieve PR metadata:
   `gh pr view <number> --json title,body,url,additions,deletions,files`
2. Retrieve the diff:
   `gh pr diff <number>`
3. For each URL found in the PR body, verify accessibility with WebFetch.
   If a URL is unreachable (network error, 403, etc.), report it as "unverifiable" rather than a must-fix.
4. Analyze the PR against the review criteria below.
5. Output the result in the format described below.

## Review Criteria

1. Reviewer-facing information
   - Can a reviewer understand the purpose, what changed, and the impact from the PR body alone?
   - Is the scope of the change clear?

2. Sources and references
   - Are official documentation URLs or other authoritative sources provided to justify configuration values, tool choices, or version selections?
   - This is especially important for dotfiles / infrastructure changes where "why this value" matters.

3. Intent and rationale
   - Does the PR explain not just what changed but why?
   - Is the motivation (bug, feature request, tech debt, compliance, etc.) stated?

4. Link validity
   - Do all URLs in the PR body resolve to the expected content?
   - Do anchor links point to the correct section?

5. Title / body / diff consistency
   - Does the PR title accurately reflect the change?
   - Is there any contradiction between the body description and the actual diff?

6. Diff coverage
   - Does the PR body account for all files and changes in the diff?
   - Are there unexplained changes?

## Output Format

```
## PR Self-Check Result

### Must Fix
- (Critical issues: broken links, title/content mismatch, missing rationale for important changes)

### Should Fix
- (Recommended improvements: missing source URLs, unclear scope description)

### Nice to Have
- (Minor polish: wording, formatting)

### Verdict
PASS | NEEDS_IMPROVEMENT
```

If there are no items for a severity level, write "None."

## Important Notes

- This is a single-pass check. Do not re-run the check after fixes.
- Focus on the PR as a communication artifact for human reviewers, not on code correctness (CI covers that).
- When in doubt, prefer "Should Fix" over "Must Fix" to avoid blocking on subjective issues.
