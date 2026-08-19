# PR Guidelines

Quality criteria for pull requests. Follow these when writing a PR body
and when self-reviewing your own PR.

A PR body is a summary that helps a reviewer decide, not a complete
record of the change: everything else lives in the diff, the issue, or
a linked source. It serves two audiences — the reviewer deciding now,
and the future reader who reaches this PR from `git log` or blame. Both
need why the change was made and the shape of the decision behind it;
neither needs what the diff already shows.

A body is ready when it holds all five properties below. Every rule in
the five property sections belongs to exactly one of them, and within a
section the top-level line is the rule while the lines beneath it
qualify it. `/pr-selfcheck` evaluates the properties one at a time.

- Decidable — a reviewer can decide approve or reject from the body
  alone, reading top-down
- Grounded — every claim is checkable on the evidence the body itself
  carries
- Necessary — the body carries nothing the PR already carries
  elsewhere (the diff, its commits, the Checks panel, output an
  automation posted on it), states each thing once, and takes from a
  linked source no more than the summary that survives the link going
  dead
- Scoped — the diff carries only what the stated intent needs, and the
  body accounts for all of it
- Conformant — the body renders and behaves as intended on GitHub

## Decidable

- State what changed and why (bug, feature, tech debt, compliance,
  etc.)
  - The body alone conveys the intent and lets a reviewer understand
    the purpose, what changed, and the impact
- Give the shape of the decision: the approach taken vs. the approaches
  rejected, and risks or things a reviewer should watch out for
  - "Approaches rejected" covers design alternatives weighed for the
    delivered design
- Inverted pyramid — place the most important information first
  - A reviewer reading only the first few lines can tell what kind of
    PR this is and where to focus
- Progressive disclosure — surface only what a reviewer needs to decide
  - Implementation details and full alternatives narrative move behind
    a link or to a "Notes" / "Background" section at the end
- In a bulleted section, the top level carries the change or claim
  itself, so the section reads from its top-level lines alone
  - Supporting material — rationale, evidence, the behavior this change
    replaces, mechanical consequences, and the like — does not displace
    it from the top level
- When one top-level item in a section supports, qualifies, or follows
  from another, it belongs beneath that one rather than beside it
  - A long flat list is usually a hierarchy that was never encoded
- Future work, out-of-scope follow-ups, and "next PR" notes belong at
  the end of the body (e.g., in a "Follow-up" / "Notes" section)
  - Do not surface them in the opening sections (purpose, scope,
    summary), where they compete with the approve/reject decision
- Tables must stand alone
  - Give each table a caption or a one-line lead-in that tells the
    reader what it shows (e.g., "Alert firings in the past 7 days")
  - A reader who skips the surrounding prose still understands what the
    table represents
  - Avoid placing tables mid-sentence where their meaning depends on
    parsing the prose around them

## Grounded

- Attempt every verification within reach before drafting the
  Verification section: shell commands, API calls, file inspection,
  mocked failure modes, simulated missing-config tests
  - Punting reachable items to "Pending" or "User to verify" is itself
    the violation
  - Overstating what is "untestable" is the common failure mode
- List only items actually verified, each carrying its evidence: a
  command, output excerpt, exit code, or log line
  - A code block or sub-bullet attached to the item counts as evidence
    the item carries
  - When the item covers documentation or prose and no command applies,
    name what it was checked against (the source, the spec, the linked
    issue)
- Items that genuinely require interactive UI, user-only credentials,
  target environments unreachable from a shell, or the live session
  itself must be clearly distinguished with reproduction steps and a
  one-line reason why the author could not verify them
- A negative or absence claim ("no X remains", "該当なし") shows the
  query it rests on and the scope it examined
  - Template-mandated N/A fields are outside this rule
  - The shown query covers the whole claim — a regex anchored to line
    start or end, a single literal where the claim covers a family of
    spellings, or a path filter narrower than the claim does not
- Provide official documentation URLs or other authoritative sources
  that justify configuration values, tool choices, or version
  selections
  - Especially important for dotfiles / infrastructure changes where
    "why this value" matters
- A claim about the behavior of a tool, service, or platform this diff
  does not modify carries a link to or citation of a primary source (a
  man page section or `--help` output counts)
- A causal claim asserting a mechanism a reader cannot check from the
  diff ("because X locks the table") carries evidence or a source
- A value presented as a measured or derived result shows or links its
  derivation
  - Identifiers and version strings are outside this rule
- Rationale attributed to a linked issue, PR, or document quotes the
  one sentence it rests on, or links to the section carrying it
- All URLs and anchor links resolve to the expected content
- The title accurately reflects the change, and the body does not
  contradict the diff

## Necessary

- Do not paraphrase the diff
  - Keep out file lists, line counts, percentage of lines removed,
    per-file summaries, and enumerations of added rules, linters,
    settings, constants, or values
  - Keep out self-paraphrase of own edits ("edited file X", "bumped
    value from A to B", "added N items", "raised timeout to M")
  - Keep out per-item rendering of a pre-flight checklist when every
    item is "N/A", collapsing it to one line
- Keep CI, lint, formatter, type-check, and build / test command
  results (`go build`, `go test`, `go vet`, `pre-commit`) out of the
  body
  - This holds whether or not the repository's CI runs them
  - Output that CI or another automation posts on the PR itself (build
    status, terraform / CDK plan output, lint and type-check results)
    stays where it was posted, and the body does not restate it
- Focus on what changes from the user's or system's perspective —
  behavior changes, new capabilities, removed limitations — rather than
  on implementation details (resources added, files touched)
- The body records the delivered design, not the path to it
  - Keep out chronological narration of implementation attempts ("first
    tried X, it failed, so Y") and records of direction changes made
    mid-implementation
  - Keep out references to the session, to plan-mode phases, or to
    individual commits within the branch
  - Keep out rejected alternatives described at implementation-attempt
    granularity
- State a fact once
  - The same environment variable name, file name, design decision, or
    summary of a linked source does not appear in two places in the
    body
- Each bullet conveys a distinct decision or outcome, not an individual
  code change
  - Bullets in the same list do not restate one another in different
    wording
- Rationale, background, or requirements that live elsewhere (issue,
  design doc, ADR, prior PR, official spec) are summarized under a
  link, not copied
  - A bare link is itself a defect: write the shortest summary that
    survives the link going dead
  - Anything past that point is duplication
- When the diff is self-explanatory — documentation or config edits
  whose changed lines a reviewer can read directly, especially in the
  team's own language — keep the body to what the diff cannot convey
  (rationale, scope boundary)
  - When nothing remains to add, one line such as "realigned stale
    wording with the actual code/config" is a complete description
- A section heading grants no exemption
  - "diff から読み取れない設計判断", "補足", or "詳細" does not excuse its
    contents from this property — each paragraph under it still has to
    be needed for the decision
- A body that is long because every part of it is needed is correct as
  it is, and length itself is never a finding

## Scoped

- Describe the boundary of the change and call out anything
  intentionally left out of scope
- The PR diff itself is a deliverable
  - Edits, reformats, renames, and "while I'm here" cleanups that fall
    outside the PR's stated scope should not appear in the diff
  - Out-of-scope hunks force the reviewer to separate "intent vs
    incidental" and inflate review load
  - Adjacent incidental fixes (an obvious typo) are tolerable in
    moderation, but the default is to leave them for a separate PR
- The body conveys the holistic intent of the change — what the PR is
  trying to achieve across the whole diff — accounts for every file and
  change in it, and leaves no unexplained hunks
- The body names a verification mechanism — CI, manual test steps, or
  another check — for the code paths the diff changes
  - The test is whether the body makes that claim
  - Judging how adequate the coverage is belongs to code review
- Keep the PR self-contained
  - Verification items, acceptance criteria, and follow-up actions that
    depend on changes outside this PR's diff (other repos, downstream
    releases, E2E flows) belong in the parent issue
- A description that keeps growing is a prompt to ask whether the diff
  should be split into finer-grained PRs

## Conformant

- The title is a one-line summary in the team's review language
  - Any content that doesn't fit on one line — including issue
    references (`#123`, `org/repo#123`) — belongs in the body, not the
    title
- Language follows the target repository, not the conversation
  - Honor any explicit rule in the repo's `CLAUDE.md` / `AGENTS.md`
    first, otherwise match the existing PR / commit history
  - Don't let the language of the chat with the user decide
- Do NOT use auto-close keywords (`Closes`, `Fixes`, `Resolves`)
- Checkbox syntax (`- [ ]` / `- [x]`) is reserved for verification
  items
  - `- [x]` marks one the author verified
  - `- [ ]` marks one the user is expected to verify or act on later so
    it can be ticked off
  - `- [ ]` carrying a one-line reason marks an author-owed item that
    Grounded exempts as unverifiable by the author
  - Prose statements do not take a checkbox
- Inside GitHub issues, pull requests, and discussions — bodies and
  comments alike, that is Markdown posted through the GitHub web UI —
  do not hard-wrap paragraphs or list items
  - Write each paragraph as a single line and let the browser wrap it
  - Use blank lines for paragraph breaks
  - GitHub Flavored Markdown renders soft line breaks inside a
    paragraph as visible breaks only in these contexts
    ([basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax))
  - Plain Markdown files (READMEs, ADRs, this guidelines file itself,
    and any other in-repo documentation) follow standard Markdown
    rendering and may be hard-wrapped for file-side readability

## PR Body Template (fallback)

Use this scaffold when the target repository has no `pull_request_template.md`.
Repository templates always win — do not overlay this on top of one.
Section names stay English; body language follows the repo (see
Conformant above). Purpose / Key changes / Verification is the minimum.
Sources and issue links are inlined only when applicable.

```
## Purpose

<1-3 sentences on why the change is being made — problem it solves,
what prompted it, intended outcome. Not a paraphrase of the diff.>

## Key changes

<3-5 bullets, each a distinct decision or user-visible outcome. Do
not enumerate files, line counts, or per-file summaries — the diff
already shows those.>

## Verification

- [x] <command executed> → <observed output excerpt>              # author-verified with evidence
- [ ] <item still owed by author> — <reason it could not be run>  # author-owed, pending
- [ ] <item the user will confirm later>                           # user-owed, actionable checkbox
```
