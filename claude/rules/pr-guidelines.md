# PR Guidelines

Quality criteria for pull requests. Follow these when writing a PR body
and when reviewing your own PR.

## Writing Style

- Summarize the change at a high level. Do not mirror the diff line-by-line.
- Keep bullet points few and meaningful. Each bullet should convey a
  distinct decision or outcome, not an individual code change.
- Focus on what changes from the user's or system's perspective — behavior
  changes, new capabilities, removed limitations, etc. — rather than
  listing implementation details (resources added, files touched).
- Anything a reviewer can see by reading the diff does not need to be
  restated in the body. Focus on context the diff cannot convey: why the
  change was made, trade-offs considered, and things to watch out for.
- If a linked issue or doc already explains the background, keep the PR
  body to a brief pointer and delegate detail there. Do not restate.
- Do not hard-wrap paragraphs or list items at a fixed column width.
  GitHub Flavored Markdown renders soft line breaks inside a paragraph
  as visible breaks (or runs them together awkwardly), so a body
  wrapped at ~70 chars looks broken on the web. Write each paragraph
  as a single line and let the browser wrap it. Use blank lines for
  paragraph breaks. The same rule applies to issue bodies and PR /
  issue comments.

## PR Body Checklist

When writing a PR body, cover every applicable item:

1. Purpose and motivation
   - State what changed and why (bug, feature, tech debt, compliance, etc.).
   - A reviewer should understand the intent from the body alone.

2. Scope
   - Clearly describe the boundary of the change.
   - Call out anything intentionally left out of scope.
   - A PR should be a self-contained unit. Verification items, acceptance
     criteria, and follow-up actions that depend on changes outside this
     PR's diff (other repos, downstream releases, E2E flows) belong in
     the parent issue, not in the PR body.

3. Sources and references
   - Provide official documentation URLs or other authoritative sources
     that justify configuration values, tool choices, or version selections.
   - Especially important for dotfiles / infrastructure changes where
     "why this value" matters.

4. Issue linking
   - Do NOT use auto-close keywords (`Closes`, `Fixes`, `Resolves`).

5. Verification
   - Describe only what was actually verified under "confirmed" items.
   - Do not claim verification that was not performed.
   - When the change affects environments that CI cannot replicate
     (e.g., Claude Code web, external services), include manual test
     steps the reviewer can follow to verify in the real environment
     before merging.

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
   - Is content duplicated from a linked issue or doc? If so, remove it
     and let the linked source explain.

8. Verification completeness
   - Is every changed code path covered by CI, manual test steps in the
     PR body, or another verification mechanism?
   - Are there paths that only run in a specific target environment
     (e.g., Claude Code web, external services) without a stated plan
     to verify them?
   - Are all verification items scoped to this PR's diff alone?
     Cross-component or E2E items belong in the parent issue.
