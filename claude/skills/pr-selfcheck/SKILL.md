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
   `gh pr view <number> --json title,body,url,additions,deletions,files,baseRefName`
1. Retrieve the diff:
   `gh pr diff <number>`
1. When verifying a body claim needs file contents at the PR head,
   run `git fetch origin pull/<number>/head` once and read via
   `git show FETCH_HEAD:<path>`. When a body claim asserts repository
   state at the PR head and shows the query it rests on, re-run that
   query with `FETCH_HEAD` as its tree-ish argument
   (`git grep <pattern> FETCH_HEAD`). A result that contradicts the
   claim is a Fix; incidental differences such as line numbers or
   unrelated new hits are not a contradiction. A query that takes no
   tree-ish argument cannot be re-run at the PR head, and the claim
   resting on it is unverifiable. Do not create local branches and do
   not run `git branch -D`/`-d` (branch deletion blocks on a permission
   prompt)
1. When a check needs a file as it stood before the change, read it at
   the merge base of the PR head and the PR's own base branch. Run
   `git fetch origin <baseRefName>` with the value the metadata step
   returned and capture `git rev-parse FETCH_HEAD` as the base tip, then
   run `git fetch origin pull/<number>/head`. Take
   `git merge-base <base tip> FETCH_HEAD` and read through
   `git show <merge base>:<path>`. Keep that order: each fetch repoints
   `FETCH_HEAD`, and ending on the head is what leaves the form above
   reading the head for every later check. The default branch is not
   that merge base once anything has landed since the branch was cut,
   and a change already merged there reads as text the diff did not add
1. Locate and read `pr-guidelines.md`, bundled with the `git-workflow`
   skill, to load the five properties the PR body is judged against
1. For each URL found in the PR body, fetch it with WebFetch and
   compare what comes back against what the body cites the URL for. A
   fetch that returns no comparable content makes the URL unverifiable
   — a network error, a timeout, a permission denial, any auth-gated
   response (WebFetch is unauthenticated, so a correct link to a
   private repository, issue, or dashboard answers with 404, 403, 401,
   or a login page), a 429 or 5xx, and a domain `WebFetch` is denied
   all land here. A Fix only when fetched content contradicts the
   citation
1. Walk the five properties one at a time, in the order
   `pr-guidelines.md` states them, judging the PR against that
   property's rules and the severity table below
1. Run the density pass described below over the body's list items and
   paragraphs. It is a count, not a judgement, and it does not depend
   on the body's language
1. Output the result in the format described below, reporting a line
   for every property including those with no finding

## Severity

| Severity | Condition |
| --- | --- |
| Fix | Acting on it is required before the PR is ready: a reviewer acting on the body would be misled about what the change does, would find in the diff a change the body did not prepare them for, or would treat a claim the change rests on as settled when the body does not carry what settles it |
| Note | Surfaced for the reader's judgement, and the reader decides whether to act: a blemish that changes nothing for the reviewer, or a finding the checker is not confident about, stated with the reason for the doubt |
| Unverifiable | A check that produced nothing comparable against the claim (the `FETCH_HEAD` and URL steps above). Reported as unverifiable, never Fix |

## Hard-wrap detection (GitHub-posted markdown)

Conformant forbids hard-wrapping in GitHub-posted markdown. Apply this
parser rather than judging line breaks by eye. Each violation it finds
is a Fix.

A "block marker" below means a line starting with any of: `#`, `-`,
`*`, `+`, a digit followed by `.` (e.g. `1.`), `>`, `|`, four spaces
of indent, or a fenced code marker (``` or ~~~).

Violations:

- Two or more consecutive non-empty lines with no blank line between them, where neither line begins with a block marker (this catches paragraph-internal soft breaks while leaving tight lists, headings, and other block constructs alone)
- An indented continuation line directly following a list-item line (`- `, `* `, `+ `, or `N. `) with no blank line between them, where that indented line does not itself begin with `- `, `* `, `+ `, or `N. ` — a blank-line gap before the indent denotes a valid continuation paragraph and is not a violation

Excluded from detection to avoid false positives:

- Inside fenced code blocks (track open / close of paired ``` or ~~~ fences)
- GFM tables in either form: rows whose first and last non-whitespace characters are `|`, or pipeless rows recognized by the `---|---` divider line directly below the header row
- HTML comments (`<!-- ... -->`)
- Blockquotes (lines starting with `> `)

## Density pass

Decidable asks each item to carry one claim at the shortest length that
lands it. Apply the count below rather than judging length by eye. Each
violation it finds is a Fix.

A sentence terminator is `.`, `。`, `!`, `?`, `！`, or `？`. Ignore one
that falls inside inline code, a fenced block, a URL, a version string,
or a decimal number, and ignore a trailing terminator, so a one-sentence
item counts zero.

Violation:

- A list item whose own text carries one or more sentence terminators after ignoring the trailing one — that is, two or more sentences

Excluded from detection:

- A `- [x]` or `- [ ]` item, whose extra sentences are the evidence Grounded requires it to carry
- Sub-bullets, which are counted as their own items rather than as part of the parent
- Fenced code blocks, GFM table rows, HTML comments, and blockquotes

The companion rule — a paragraph enumerating three or more parallel
items of the same kind belongs in a list — takes judgement rather than a
count, so weigh it against the severity table instead of reporting it
from this pass.

## Output Format

```
## PR Self-Check Result

### Fix
- [<property>] <finding>

### Note
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

Write "None." under any of the three finding headings that has no
items, Unverifiable included. The verdict is NEEDS_IMPROVEMENT when any
Fix item is present, PASS otherwise.

## Important Notes

- This check may be re-run after fixes (e.g., Phase 1 retry, Phase 3 consistency check in the git workflow)
- Focus on the PR as a communication artifact, not on code correctness (CI covers that)
