# PR Guidelines

Quality criteria for pull requests. Follow these when writing a PR body
and when reviewing your own PR.

## Writing Style

A PR body is a summary that helps a reviewer decide, not a complete
record of the change. Follow the Essence-first principle: surface
what a reviewer needs to approve or reject the PR; everything else
lives in the diff, the issue, or a linked source.

### Title

- One-line summary in the team's review language.
- Place issue references (`#123`, `org/repo#123`) in the body, not
  the title — GitHub already surfaces the linked issue panel.

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
  This also applies to information that CI or automation posts on
  the PR (build status, terraform/CDK plan output, lint results,
  type check results): do not restate those facts in the body —
  let the bot comments and checks panel speak for themselves.
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
- Tables must stand alone. Give each table a caption or a one-line
  lead-in that tells the reader what it shows (e.g., "Alert firings
  in the past 7 days"). A reader who skips the surrounding prose
  should still understand what the table represents. Avoid placing
  tables mid-sentence where their meaning depends on parsing the
  prose around them.
- Future work, out-of-scope follow-ups, and "next PR" notes belong
  at the end of the body (e.g., in a "Follow-up" / "Notes" section).
  Do not surface them in the opening sections (purpose, scope,
  summary), where they compete with the approve/reject decision.
  Reviewer attention is limited; the most-actionable information for
  this PR should reach the reader first.
- Inside GitHub PR / issue bodies and PR / issue comments only — that
  is, Markdown posted through the GitHub web UI — do not hard-wrap
  paragraphs or list items. Write each paragraph as a single line and
  let the browser wrap it; use blank lines for paragraph breaks. GitHub
  Flavored Markdown renders soft line breaks inside a paragraph as
  visible breaks (or runs lines together awkwardly) only in these
  contexts, so a body wrapped at ~70 chars looks broken on the web.
  Plain Markdown files (READMEs, ADRs, this guidelines file itself,
  and any other in-repo documentation) follow standard Markdown
  rendering — single line breaks inside a paragraph are ignored — so
  they may be hard-wrapped for file-side readability.
- DO / DON'T example for a paragraph in a PR / issue body:

  DO (single line, the browser wraps it):

  ````
  Fix the broken X path so Y stops emitting spurious diffs.
  ````

  DON'T (paragraph hard-wrapped at column width):

  ````
  Fix the broken X path so Y stops emitting
  spurious diffs.
  ````

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
   - Attempt every verification within reach before drafting this
     section: shell commands, API calls, file inspection, mocked
     failure modes, simulated missing-config tests. Punting reachable
     items to "Pending" or "User to verify" (see below) is itself the
     violation — overstating what is "untestable" is the common
     failure mode.
   - List only items actually verified, with evidence (command output,
     exit code, log excerpt).
   - Items that genuinely require interactive UI, user-only
     credentials, target environments unreachable from a shell, or
     the live session itself must be clearly distinguished from the
     already-verified ones, with reproduction steps and a one-line
     reason why the author could not verify them. Follow the
     repository's PR template if it defines a structure; otherwise
     use any organization that makes the distinction unambiguous
     (separate subsection, prefix, etc.) — the section name itself
     is not prescribed. Scope still applies (§2): items that depend
     on changes outside this PR's diff belong in the parent issue,
     not here.
   - Use `- [ ] …` markdown checkboxes for items the user is
     expected to verify or act on later, so they can be ticked off
     after completion. This applies regardless of section name or
     structure.
   - Why over what applies to Verification too. Do not record items
     that the diff or GitHub UI already shows: line counts,
     percentage of lines removed, `wc -l` of a file you edited, the
     list of changed files, or a paraphrase of your own edits. List
     only what an external resource confirms — command output, API
     responses, log excerpts, UI behavior, etc.

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
   - Did the author attempt the verifications they could reach
     (shell, API, mocked failures), or punt them to "Pending" /
     "User to verify"? Items reachable from a shell or API belong
     in the verified list.
   - Is every changed code path covered by CI, manual test steps in the
     PR body, or another verification mechanism?
   - Are there paths that only run in a specific target environment
     (e.g., Claude Code web, external services) without a stated plan
     to verify them?
   - Are all verification items scoped to this PR's diff alone?
     Cross-component or E2E items belong in the parent issue.
