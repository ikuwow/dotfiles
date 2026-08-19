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
   state at the PR head and shows the query it rests on, re-run it as
   `git grep <pattern> FETCH_HEAD`; incidental differences such as line
   numbers or unrelated new hits are not a contradiction. Do not create
   local branches and do not run `git branch -D`/`-d` (branch deletion
   blocks on a permission prompt)
1. Read `~/.claude/skills/git-workflow/pr-guidelines.md` to load the
   five properties the PR body is judged against
1. For each URL found in the PR body, fetch it with WebFetch. A host
   that does not answer (network error, timeout, 403) makes the URL
   unverifiable; a 404 from a host that answered, or content that
   contradicts what the body cites the URL for, is Must Fix
1. Walk the five properties one at a time, in the order
   `pr-guidelines.md` states them, judging the PR against that
   property's rules and the severity table below
1. Output the result in the format described below, reporting a line
   for every property including those with no finding

## Severity

| Verdict | Condition |
| --- | --- |
| Must Fix | An objective presence or absence test on the body, or a contradiction confirmed against a checked source (the diff, `FETCH_HEAD`, a fetched URL) |
| Should Fix | A judgment of degree: redundancy, ordering, bullet granularity |
| Nice to Have | Wording or formatting with no effect on the decision |
| Escalation | Two or more Should Fix within one property escalates that property to Must Fix |
| Unverifiable | An unreachable URL, or a query with no tree-ish form. Reported as unverifiable, never Must Fix |

## Hard-wrap detection (GitHub-posted markdown)

Conformant forbids hard-wrapping in GitHub-posted markdown. Apply this
parser rather than judging line breaks by eye.

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
- [<property>] <finding>

### Should Fix
- [<property>] <finding>

### Nice to Have
- [<property>] <finding>

### Unverifiable
- [<property>] <item, and why it could not be checked>

### Property walk
- Decidable: <one line>
- Grounded: <one line>
- Necessary: <one line>
- Scoped: <one line>
- Conformant: <one line>

### Verdict
PASS | NEEDS_IMPROVEMENT
```

If there are no items for a severity level, write "None."

## Important Notes

- This check may be re-run after fixes (e.g., Phase 1 retry, Phase 3 consistency check in the git workflow)
- Focus on the PR as a communication artifact, not on code correctness (CI covers that)
