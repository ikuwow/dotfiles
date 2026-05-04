# PR Guidelines

Quality criteria for pull requests. Follow these when writing a PR body
and when reviewing your own PR.

## Writing Style

A PR body is a summary that helps a reviewer decide, not a complete
record of the change. Follow the Essence-first principle: surface
what a reviewer needs to approve or reject the PR; everything else
lives in the diff, the issue, or a linked source.

### Four principles

- Why over what — The diff already shows what changed. The body
  explains why, and the shape of the decision (the approach taken
  vs. approaches rejected, what was deliberately left out of scope,
  risks or things a reviewer should watch out for). Do not paraphrase
  the diff (file lists, "added X to Y", per-file summaries).
- Single source of truth (DRY) — If the rationale, background, or
  requirements live elsewhere (issue, design doc, ADR, prior PR,
  official spec), do not duplicate them. Replace with a one-line
  summary plus a link. Two copies drift apart over time.
- Inverted pyramid — Place the most important information first. A
  reviewer reading only the first few lines should be able to tell
  what kind of PR this is and where to focus.
- Progressive disclosure — Surface only what a reviewer needs to
  decide. Move implementation details, history, or full alternatives
  narrative behind a link or to a "Notes" / "Background" section at
  the end.

### Style rules

- Keep bullet points few and meaningful. Each bullet should convey a
  distinct decision or outcome, not an individual code change.
- Focus on what changes from the user's or system's perspective —
  behavior changes, new capabilities, removed limitations, etc. —
  rather than listing implementation details (resources added, files
  touched).
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

7. Conciseness (Essence-first)
   - Is the body a high-level summary rather than a line-by-line
     restatement of the diff?
   - Does any sentence paraphrase facts the diff already shows
     (file lists, "added X to Y", per-file summaries)? If so,
     remove it. (Why over what)
   - Is content duplicated from a linked issue, doc, or prior PR?
     Replace with a one-line summary plus link. (Single source of
     truth)
   - Does the reader hit the most important information in the first
     few lines? (Inverted pyramid)
   - Is implementation detail, history, or alternatives narrative
     mixed into the main body? Move it to a "Notes" / "Background"
     section at the end. (Progressive disclosure)
   - Are bullet points few and meaningful, each conveying a distinct
     point?

8. Verification completeness
   - Is every changed code path covered by CI, manual test steps in the
     PR body, or another verification mechanism?
   - Are there paths that only run in a specific target environment
     (e.g., Claude Code web, external services) without a stated plan
     to verify them?
   - Are all verification items scoped to this PR's diff alone?
     Cross-component or E2E items belong in the parent issue.
