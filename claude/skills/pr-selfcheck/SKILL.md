---
name: pr-selfcheck
description: Perform a self-review of a PR before requesting human review. TRIGGER when user invokes /pr-selfcheck or when the git workflow reaches the self-review step after PR creation. Accepts a PR number as an argument.
model: sonnet
effort: medium
context: fork
agent: general-purpose
---

# PR Self-Check

Perform a self-review of the specified PR to catch issues before a human reviewer sees it.

## Steps

1. Retrieve PR metadata:
   `gh pr view <number> --json title,body,url,additions,deletions,files`
1. Retrieve the diff:
   `gh pr diff <number>`
1. For each URL found in the PR body, verify accessibility with WebFetch
   If a URL is unreachable (network error, 403, etc.), report it as "unverifiable" rather than a must-fix.
1. Analyze the PR against the review criteria below
1. Output the result in the format described below

## Review Criteria

Evaluate the PR against the PR Body Checklist defined in `pr-guidelines.md`.

In addition to the high-level checklist, apply the following concrete
signals so detection does not rely on subagent interpretation alone.

### Redundancy / essence-first signals

Flag each as Should Fix; if multiple signals fire across the body,
escalate to Must Fix.

- Sentences or bullets that paraphrase what the diff already shows ("edited file X", "bumped value from A to B", "added N items", per-file summaries)
- CI / lint / type-check / `go build` / `go test` / `go vet` / `pre-commit` results recorded in the Verification section (the Checks panel and bot comments are the authoritative source)
- The same fact (environment variable name, file name, design decision, summary of a linked source) repeated in multiple places in the body
- Bullets in the same list that restate the same decision or fact in different wording, with no distinct information per item
- Content copied verbatim from a design doc, spec, linked issue, or primary source where a one-line summary plus link would suffice

When the implementation-summary section exceeds ~10 lines, or the
whole body (excluding template-mandated sections) exceeds ~30 lines,
re-examine the body against the signals above before deciding their
severity.

### Hard-wrap detection (GitHub-posted markdown)

For PR bodies, PR comments, issue bodies, and issue comments, GitHub
Flavored Markdown renders soft line breaks inside a paragraph as
visible breaks. Blank lines between paragraphs serve as paragraph
separators and are allowed. Flag each violation as Should Fix;
multiple violations across the body escalate to Must Fix.

A "block marker" below means a line starting with any of: `#`, `-`,
`*`, `+`, a digit followed by `.` (e.g. `1.`), `>`, `|`, four spaces
of indent, or a fenced code marker (``` or ~~~).

Violations:

- Two or more consecutive non-empty lines with no blank line between them, where neither line begins with a block marker (this catches paragraph-internal soft breaks while leaving tight lists, headings, and other block constructs alone)
- An indented continuation line directly following a list-item line (`- `, `* `, `+ `, or `N. `) with no blank line between them; a blank-line gap before the indent denotes a valid continuation paragraph and is not a violation

Excluded from detection to avoid false positives:

- Inside fenced code blocks (track open / close of paired ``` or ~~~ fences)
- GFM tables in either form: rows whose first and last non-whitespace characters are `|`, or pipeless rows recognized by the `---|---` divider line directly below the header row
- HTML comments (`<!-- ... -->`)
- Blockquotes (lines starting with `> `)

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

- This check may be re-run after fixes (e.g., Phase 1 retry, Phase 3 consistency check in the git workflow)
- Focus on the PR as a communication artifact for human reviewers, not on code correctness (CI covers that)
- When in doubt, prefer "Should Fix" over "Must Fix" to avoid blocking on subjective issues
