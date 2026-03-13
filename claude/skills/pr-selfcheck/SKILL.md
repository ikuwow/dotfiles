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

Evaluate the PR against the Review Criteria defined in `pr-guidelines.md`.
Read that file before starting the review.

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
