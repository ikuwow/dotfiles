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
1. When verifying a body claim needs file contents at the PR head,
   run `git fetch origin pull/<number>/head` once and read via
   `git show FETCH_HEAD:<path>`. When a body claim asserts repository
   state at the PR head and shows the query it rests on, re-run that
   query against `FETCH_HEAD` and report a mismatch as Must Fix. Do
   not create local branches and do not run `git branch -D`/`-d`
   (branch deletion blocks on a permission prompt)
1. Read `~/.claude/skills/git-workflow/pr-guidelines.md` to load the PR Body Checklist
1. For each URL found in the PR body, verify accessibility with WebFetch
   If a URL is unreachable (network error, 403, etc.), report it as "unverifiable" rather than a must-fix.
1. Analyze the PR against the review criteria below
1. Output the result in the format described below

## Review Criteria

Evaluate the PR against the PR Body Checklist loaded in Step 4 (`~/.claude/skills/git-workflow/pr-guidelines.md`).

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
report the overrun itself as Should Fix (pr-guidelines: Length
budget), and re-examine the body against the signals above to decide
what to cut and whether to escalate.

### Process-record signals

Applies to the PR body only. Flag each as Should Fix; if multiple
signals fire across the body, escalate to Must Fix.

- Chronological narration of implementation attempts ("first tried X, it failed, so Y")
- Records of direction changes made mid-implementation
- References to the session, to plan-mode phases, or to individual commits within the branch
- Rejected alternatives described at implementation-attempt granularity rather than as design alternatives weighed for the delivered design

### Claim-grounding signals

Applies to the PR body only. The forked self-review has no access to
the authoring session, so a claim is judged on the evidence the body
itself carries, never on whether the author is likely to have run the
check.

Flag each of these as Must Fix on a single occurrence:

- A verification item marked complete whose line carries no command, output excerpt, exit code, or log line; when the diff is documentation or prose only and no command applies, naming what the item was checked against (the source, the spec, the linked issue) satisfies this
- A negative or absence claim ("no X remains", "該当なし", "影響なし") that does not show the query, command, or enumeration it rests on

Flag each of these as Should Fix; if multiple signals fire across the
body, escalate to Must Fix:

- A claim about external tool, service, or platform behavior stated without a link to a primary source
- A causal claim about the system under change ("because X locks the table", "this keeps Y traceable") with no evidence or source attached
- A value presented as a measured or derived result whose derivation is neither shown nor linked; identifiers and version strings are not in scope
- Rationale attributed to a linked issue, PR, or document without quoting the sentence it rests on
- An absence claim whose shown query could under-match its own scope, through a line anchor, a single pattern, or a path filter narrower than the claim

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
