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
- If a linked issue, doc, or companion PR (multi-repo change with a
  primary PR carrying the rationale) already explains the background,
  keep the PR body to a brief pointer and delegate detail there. Do
  not restate.
- Do not hard-wrap paragraphs or list items at a fixed column width.
  GitHub Flavored Markdown renders soft line breaks inside a paragraph
  as visible breaks (or runs them together awkwardly), so a body
  wrapped at ~70 chars looks broken on the web. Write each paragraph
  as a single line and let the browser wrap it. Use blank lines for
  paragraph breaks. The same rule applies to issue bodies and PR /
  issue comments.
- Do not paraphrase the diff. Lists of files changed, "added X to Y",
  "renamed A → B", per-file change summaries — anything a reviewer
  recovers by reading the diff itself — does not belong in the body.
  Refer to the diff for "what changed"; the body explains "why" and
  the decisions the diff cannot show.
- Separate PR-direct content from supplementary context. The main
  body covers only what the reviewer needs to evaluate this PR
  (purpose, decisions made, verification). Background not required
  to evaluate the diff (incident history, the full alternatives
  exploration, design narrative) goes in a separate "Notes" or
  "Background" section at the end, or in a linked issue, so the
  reviewer can skip it.

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
   - Actively attempt every verification within reach before drafting
     the Verification section: shell commands, API calls, file
     inspection, mocked reproduction of the failure mode, simulated
     missing-config tests, etc. The most common failure mode this
     rule prevents is the author overestimating what is "untestable"
     and underestimating what shell-level reproduction can cover.
     Reaching for "Pending" / "deferred" without first attempting
     is itself the violation.
   - The Verification section lists only items actually verified,
     with evidence (command output, exit code, log excerpt).
   - Items that genuinely require interactive UI, user-only
     credentials, target environments unreachable from a shell, or
     the live session itself go under a separate "User to verify"
     subsection with explicit reproduction steps and a one-line
     reason why the author could not verify them.

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
   - Does the body paraphrase the diff (file lists, "added X to Y",
     per-file summaries)? If so, remove — the reviewer reads the diff.
   - Are bullet points few and meaningful, each conveying a distinct point?
   - Is supplementary context (background, full alternatives narrative,
     incident history) mixed into the main body? If so, move it to a
     "Notes" / "Background" section at the end, or link an external doc.
   - Is content duplicated from a linked issue or doc? If so, remove it
     and let the linked source explain.

8. Verification completeness
   - Is every changed code path covered by CI, manual test steps in the
     PR body, or another verification mechanism?
   - Did the author actually attempt the verifications they could reach
     (shell-level reproduction, API calls, mocked failure modes), or
     did they punt verifiable items to "Pending" / "deferred" / "User
     to verify"? Items mechanically reachable from a shell or API
     belong in the author-verified list, not "User to verify".
   - Are there paths that only run in a specific target environment
     (e.g., Claude Code web, external services) without a stated plan
     to verify them?
   - Are all verification items scoped to this PR's diff alone?
     Cross-component or E2E items belong in the parent issue.
