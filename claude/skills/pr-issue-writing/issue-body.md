# What an issue body holds

Criteria for the title and body of a GitHub issue. An issue has no diff
behind it, so its body is the whole record: a reader who opens it
decides from the body alone whether and how to act on it.

The repository's issue template, when one exists, sets the sections.
Otherwise a skill that prescribes the issue's format sets them, and
failing both, the body follows the order of the first list below.

## What the body carries

- Open with the problem or the request in one or two sentences, so the
  first lines tell a reader what the issue asks for
- For a problem, give the symptom, the steps that reproduce it, and the
  expected and actual behavior
- For a request, give what is wanted and the need behind it
- Where the issue asks the reader to choose between approaches, lay out
  each option with its tradeoff
- Keep the investigation that led to the issue: what was checked, what
  it showed, and what remains open
- Carry the evidence the issue rests on (an error message, a log
  excerpt, a measurement, reproduction output) in the body, even when a
  link also holds it, since the link may expire
- List what closes the issue, its tasks or acceptance criteria, as
  `- [ ]` items, and tick each one done as `- [x]`
- Keep references to the chat session and to plan-mode phases out,
  since a reader of the issue cannot see them

## Grounding

- State a cause not yet established as a hypothesis, with the evidence
  that points to it
- Back a claim about how an external tool or service behaves with a
  primary source (official documentation, a man page section, `--help`
  output) or with reproduction output that shows the behavior
- Show the query and the scope behind a negative or absence claim ("no
  X remains")
- Check that every URL resolves to the content it is cited for
- Summarize background that lives elsewhere (another issue, a PR, a
  design document) under its link, in the shortest form that survives
  the link going dead

## Form

- The title is a one-line summary of the problem or request, and issue
  references and other detail go in the body
- The language follows the target repository: its `CLAUDE.md` or
  `AGENTS.md` first, otherwise its existing issues
- Write each paragraph and each list item as a single line, with a
  blank line between paragraphs, since GitHub renders a line break
  inside an issue body as a visible break
- Put one claim in each list item, and nest what supports a claim under
  it
- Give each table a lead-in saying what it shows
