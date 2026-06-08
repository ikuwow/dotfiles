# PR Guidelines

Quality criteria for pull requests. Follow these when writing a PR body
and when self-reviewing your own PR.

## Writing Style

A PR body is a summary that helps a reviewer decide, not a complete
record of the change. Follow the Essence-first principle: surface
what a reviewer needs to approve or reject the PR; everything else
lives in the diff, the issue, or a linked source.

The title is a one-line summary in the team's review language. Any
content that doesn't fit on one line — including issue references
(`#123`, `org/repo#123`) — belongs in the body, not the title.

### Principles

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
- Diff scope discipline — The PR diff itself is a deliverable.
  Edits, reformats, renames, and "while I'm here" cleanups that fall
  outside the PR's stated scope should not appear in the diff. Out-
  of-scope hunks force the reviewer to separate "intent vs incidental"
  and inflate review load. Adjacent incidental fixes (an obvious
  typo) are tolerable in moderation, but the default is to leave them
  for a separate PR. The body should convey the holistic intent of
  the change — what the PR is trying to achieve across the whole
  diff — and the diff should reflect only that intent.

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
- Inside GitHub PR / issue bodies and PR / issue comments only — that
  is, Markdown posted through the GitHub web UI — do not hard-wrap
  paragraphs or list items. Write each paragraph as a single line and
  let the browser wrap it; use blank lines for paragraph breaks. GitHub
  Flavored Markdown renders soft line breaks inside a paragraph as
  visible breaks (or runs lines together awkwardly) only in these
  contexts. Plain Markdown files (READMEs, ADRs, this guidelines file
  itself, and any other in-repo documentation) follow standard Markdown
  rendering and may be hard-wrapped for file-side readability.

## PR Body Checklist

Used both when authoring a PR body and when self-reviewing it (via
`/pr-selfcheck`). Cover every applicable item — each rule is stated
once and applies to both perspectives.

1. Purpose, scope, intent
   - State what changed and why (bug, feature, tech debt, compliance,
     etc.). The body alone should convey the intent and let a reviewer
     understand the purpose, what changed, and the impact.
   - Describe the boundary of the change and call out anything
     intentionally left out of scope.
   - Keep the PR self-contained. Verification items, acceptance
     criteria, and follow-up actions that depend on changes outside
     this PR's diff (other repos, downstream releases, E2E flows)
     belong in the parent issue, not in the PR body.

2. Sources and references
   - Provide official documentation URLs or other authoritative
     sources that justify configuration values, tool choices, or
     version selections. Especially important for dotfiles /
     infrastructure changes where "why this value" matters.
   - All URLs and anchor links must resolve to the expected content.

3. Issue linking
   - Do NOT use auto-close keywords (`Closes`, `Fixes`, `Resolves`).

4. Verification
   - Attempt every verification within reach before drafting this
     section: shell commands, API calls, file inspection, mocked
     failure modes, simulated missing-config tests. Punting reachable
     items to "Pending" or "User to verify" is itself the violation —
     overstating what is "untestable" is the common failure mode.
   - List only items actually verified, with evidence (command
     output, exit code, log excerpt). Never record what the diff or
     GitHub UI already shows: line counts, `wc -l` of a file you
     edited, the list of changed files, percentage removed,
     paraphrase of own edits, or CI / lint / type-check results
     (those live in the Checks panel and bot comments).
   - Items that genuinely require interactive UI, user-only
     credentials, target environments unreachable from a shell, or
     the live session itself must be clearly distinguished with
     reproduction steps and a one-line reason why the author could
     not verify them.
   - Use `- [ ] …` markdown checkboxes for items the user is
     expected to verify or act on later, so they can be ticked off
     after completion.
   - Every changed code path is covered by CI, manual test steps in
     the PR body, or another verification mechanism. All verification
     items are scoped to this PR's diff alone; cross-component or E2E
     items belong in the parent issue.

5. Conciseness (Essence-first)
   - The principles above (Why over what, DRY, Inverted pyramid,
     Progressive disclosure, Diff scope discipline) apply directly
     here — they are not restated as separate review questions.
     A sentence that paraphrases the diff, duplicates a linked
     source, or buries the lead is a violation regardless of which
     principle names it.
   - Never include in the body:
     - Enumerations of added rules, linters, settings, constants,
       or values (visible in the diff)
     - CI job pass/fail, lint results, type-check results
     - Self-paraphrase of own edits ("edited file X", "bumped value
       from A to B", "added N items", "raised timeout to M")
     - File lists, line counts, percentage of lines removed
     - Per-item rendering of a pre-flight checklist when every item
       is "N/A" — collapse to one line
   - Bullets are few and meaningful, each conveying a distinct point.

6. Title / body / diff consistency
   - The title accurately reflects the change.
   - The body does not contradict the diff.
   - The body accounts for all files and changes in the diff; there
     are no unexplained hunks.
