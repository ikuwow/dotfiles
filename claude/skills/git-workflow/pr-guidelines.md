# PR Guidelines

Quality criteria for pull requests. Follow these when writing a PR body
and when self-reviewing your own PR.

A PR body is a summary that helps a reviewer decide, not a complete
record of the change: everything else lives in the diff, the issue, or
a linked source. It serves two audiences — the reviewer deciding now,
and the future reader who reaches this PR from `git log` or blame.

The diff is the default carrier: the body adds what the diff cannot
state and what a reader would not derive from it. No rule under
Decidable or Scoped is discharged by writing more, and none asks for a
section the diff's own content would fill. The shortest body that
leaves a reviewer able to decide is the correct one.

A body is ready when it holds all five properties below. Every rule in
the five property sections belongs to exactly one of them, and within a
section the top-level line is the rule while the lines beneath it
qualify it. `/pr-selfcheck` evaluates the properties one at a time.

- Decidable — reading top-down, a reviewer arrives at the diff knowing
  what the change is for and where their attention belongs
- Grounded — every claim is checkable on the evidence the body itself
  carries, and the body names a verification mechanism for the code
  paths the diff changes
- Necessary — read each line of the body for where else its content
  already lives, and the body carries nothing the diff, its commits,
  the Checks panel or an automation's output carry, states each thing
  once, takes from a linked source no more than the summary that
  survives the link going dead, and writes what remains at its tightest
  expression
- Scoped — the diff read against the body carries only what the stated
  intent needs and nothing the body did not lead the reader to expect,
  and the body conveys the change as a whole: a boundary the reader
  would not assume, and what it leaves to the parent issue
- Conformant — the body renders and behaves as intended on GitHub

## Decidable

- Name the change in one sentence, and add what prompted it now where
  the diff does not show it — the incident, the investigation that
  could not conclude, the request, the obligation that came due
  - The changed lines are the diff's to show, so the body names the
    change rather than describing it
- Where a design decision was weighed, the body carries its shape: the
  approach taken against the approaches rejected, and risks or things a
  reviewer should watch out for
  - A change with one obvious approach carries none of this, and
    inventing an alternative to name is itself a defect
  - "Approaches rejected" covers design alternatives weighed for the
    delivered design
- Where the diff changes something other code reaches — a function
  signature, a config key, an exit code, a file another script reads —
  name the invariant it still holds
- Inverted pyramid — place the most important information first
  - A reviewer reading only the first few lines can tell what kind of
    PR this is and where to focus
- Progressive disclosure — surface only what a reviewer needs to decide
  - Implementation details and full alternatives narrative move behind
    a link or to a "Notes" / "Background" section at the end
- The body's structure comes from the decisions the change carries, not
  from the shape of the diff. A subheading or top-level bullet standing
  for one hunk, one file, or one edited section of a document is a
  defect, and a change carrying a single decision is described in one
  paragraph under whichever section the template puts it in
  - A structure a reader could reconstruct from the diff's file list or
    hunk boundaries alone tells the reviewer nothing about where their
    attention belongs
- In a bulleted section, the top level carries the change or claim
  itself, so the section reads from its top-level lines alone
  - Supporting material — rationale, evidence, the behavior this change
    replaces, and the like — does not displace it from the top level
- When one top-level item supports, qualifies, or follows from another,
  it belongs beneath that one rather than beside it, in whichever
  section that one sits, unless another rule here places it in a
  section of its own
  - A long flat list is usually diff paraphrase; where it survives
    Necessary, it is usually a hierarchy that was never encoded
  - A section this empties loses its heading with it
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
  - Punting a reachable item to "Pending" or "User to verify" violates
    this rule
  - Overstating what is "untestable" is the common failure mode
- List only items actually verified, each carrying its evidence: a
  command, output excerpt, exit code, or log line
  - Evidence carried in a code block or sub-bullet attached to the item
    counts as evidence the item carries
  - When the item covers documentation or prose and no command applies,
    name what it was checked against (the source, the spec, the linked
    issue)
- Items that genuinely require interactive UI, user-only credentials,
  target environments unreachable from a shell, or the live session
  itself must be clearly distinguished with reproduction steps and a
  one-line reason why the author could not verify them
- The body names a verification mechanism — CI, manual test steps, or
  another check — for the code paths the diff changes
  - The test is whether the body makes that claim
  - Judging how adequate the coverage is belongs to code review
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
- Naming an external tool or service in a step the reader is meant to
  follow — verification, rollout, rollback, monitoring — asserts the
  project uses it, and the body shows what settles that: a dependency
  file, a config file, or the project's own documentation
- A value the reader would rely on to stop checking — a count that
  asserts completeness, a uniqueness claim, a coverage figure — shows or
  links its derivation
  - Identifiers, version strings, and figures that only describe the
    change are outside this rule
- Rationale attributed to a linked issue, PR, or document quotes the
  one sentence it rests on, or links to the section carrying it
- All URLs and anchor links resolve to the expected content
- The title accurately reflects the change, and the body does not
  contradict the diff

## Necessary

- Take the body a line at a time and name where else that line's content
  lives — the diff, the branch's commits, the Checks panel, a linked
  source, another line of this body, or nowhere
  - What the answer forfeits is the part it already carries: detail the
    diff or the commits show, output the Checks panel holds, a fact
    another line of the body states, and anything past the shortest
    summary a linked source needs
  - A heading is a line the walk takes, and answers for its own text
    rather than for the lines beneath it
  - A table row is a line of the walk, read with the caption or lead-in
    that says what the table shows
  - A line carrying more than one claim is answered a claim at a time,
    and each claim forfeits what its own answer names
  - A line the walk lands on is a finding whether or not a rule below
    names it, and the rules below reach lines answering `nowhere` that
    the walk does not
- After that pass, walk the body again for how densely what survived is
  written
  - A list item carrying two or more sentences is a finding: the second
    becomes a sub-bullet under the first, or it was not needed, and an
    item taking three sentences to land is usually two items
    - A verification item's evidence is exempt, since Grounded requires
      the item to carry it
  - A paragraph enumerating three or more parallel items of the same
    kind — reasons, rejected alternatives, caveats, options — is a
    finding, and the items belong in a list, one per line
    - A single claim carrying its own qualifier stays prose
- Do not paraphrase the diff
  - Keep out file lists, line counts, percentage of lines removed,
    per-file summaries, and enumerations of added rules, linters,
    settings, constants, or values
  - Keep out self-paraphrase of own edits ("edited file X", "bumped
    value from A to B", "added N items", "raised timeout to M")
  - Keep out per-item rendering of a pre-flight checklist when every
    item is "N/A" — collapse it to one line
  - Keep out mention of a change that follows mechanically from another
    change the body already states (documentation updated to match a
    code change, counts adjusted to match a removed item)
  - Name a change in a line and leave its detail to the diff, which the
    reviewer can open; spelling out what an added rule, definition, or
    table row says is detail, whether quoted, summarized, or given with
    its consequence
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
    granularity, and alternatives a reviewer would not arrive at and
    ask about
- State a fact once
  - The same environment variable name, file name, design decision, or
    summary of a linked source does not appear in two places in the
    body
  - Two bullets in one list saying the same thing in different wording
    are one fact stated twice
- Each bullet conveys a distinct decision or outcome, not an individual
  code change
- Rationale, background, or requirements that live elsewhere (issue,
  design doc, ADR, prior PR, official spec) are summarized under a
  link, not copied
  - A bare link is itself a defect: write the shortest summary that
    survives the link going dead
  - Anything past that shortest summary is duplication
- When the diff is self-explanatory — documentation or config edits
  whose changed lines a reviewer can read directly, especially in the
  team's own language — the body keeps to what the diff cannot convey,
  and neither Decidable nor Scoped asks for a rationale or boundary
  beyond that
  - When nothing remains to add, one line such as "realigned stale
    wording with the actual code/config" is a complete description
  - Apply this rule before the others in this section, so what it
    leaves is what they read
- A section heading grants no exemption
  - "diff から読み取れない設計判断", "補足", or "詳細" does not excuse its
    contents from this property — each paragraph under it still has to
    be needed for the decision
- A body long because every part of it is needed, each part at its
  tightest expression, is correct as it is
  - Raw length, and the ratio of body size to diff size, are never
    findings on their own

## Scoped

- Where the change stops short of what its intent would lead a reader
  to expect, the body says so; a boundary the reader would assume needs
  no statement
- Edits, reformats, renames, and "while I'm here" cleanups that fall
  outside the PR's stated scope should not appear in the diff
  - The PR diff itself is a deliverable, and out-of-scope hunks force
    the reviewer to separate "intent vs incidental" and inflate review
    load
  - Adjacent incidental fixes (an obvious typo) are tolerable in
    moderation, but the default is to leave them for a separate PR
- The body conveys the change as a whole: the intent behind it, and the
  parts a reader needs in order to hold that intent, with the rest left
  to the diff
  - A reader who finishes the body and then opens the diff finds what
    the body led them to expect. The expectation is of the change's
    intent, not of an inventory of where the diff touches — naming the
    edited files, sections, or hunks does not discharge this
  - Where they do not, the body and the diff disagree, and the author
    chooses which of the two moves
- Keep the PR self-contained: verification items, acceptance criteria,
  and follow-up actions that depend on changes outside this PR's diff
  (other repos, downstream releases, E2E flows) belong in the parent
  issue
- A description that keeps growing is a prompt to ask whether the diff
  should be split into finer-grained PRs

## Conformant

- The title is a one-line summary in the team's review language
  - Any content that doesn't fit on one line — including issue
    references (`#123`, `org/repo#123`) — belongs in the body, not the
    title
- Language follows the target repository, not the language of the chat
  with the user
  - Honor any explicit rule in the repo's `CLAUDE.md` / `AGENTS.md`
    first, otherwise match the existing PR / commit history
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

## Worked example: a minimal body

A design document gains a retry on one forwarding hop, and the sending
side's request spec, until then split across two places, is gathered
into a new prerequisites section. One Markdown file, 15 lines added and
7 removed, in the team's own language. The body's whole account of the
change, under whichever heading the repository's template gives it:

```
転送失敗時のリトライを設計として追加しました。

合わせて、「前提: 送信仕様」節を新設するなど文章の整理をしました。
```

The first sentence names the decision and the second names the
reorganization. Creating that section is the change; which lines moved
into it, and how the surrounding text was rewritten to point at it, are
the edits carrying it out, and the reviewer reads those in the diff.

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
