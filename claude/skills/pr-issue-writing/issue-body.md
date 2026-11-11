# What an issue body holds

Criteria for the title and body of a GitHub issue. An issue has no diff
behind it, so its body is the whole record: a reader who opens it
decides from the body alone whether and how to act on it. A security
vulnerability goes through the repository's private reporting channel
instead, since an issue may be public.

The repository's issue template, when one exists, sets the sections and
their order, and the content below goes into them. Otherwise a skill
that prescribes the issue's format sets them, and failing both, the
body carries the content below in the order listed.

## What the body carries

- State the problem or the request in one or two sentences before the
  detail that supports it
- Give what a reader needs to act: what is wrong or wanted, and why it
  matters
  - Where the problem reproduces, include the steps and the expected and
    actual behavior
- Where the issue asks the reader to choose between approaches, lay out
  each option with its tradeoff
- Where an investigation led to the issue, keep what was checked, what
  it showed, and what remains open
- Quote the part of the evidence the issue rests on (an error message,
  a log line, a measurement) in the body, even when a link holds the
  rest, since the link may expire
- Keep credentials, personal data, and customer identifiers out of the
  body, including what it quotes, since an issue may be public
- List what closes the issue, where it is already known, as `- [ ]`
  items
  - On every edit, read each `- [ ]` item against the results the
    session has seen and mark `[x]` the ones they settle, since a
    reader takes the boxes as the issue's progress and an item settled
    earlier stays unchecked until an edit marks it
  - When a comment records the result, follow it with a body edit that
    marks the item
  - An item the results leave partly open stays `- [ ]`
- Write every sentence so it reads without the chat session or the plan
  that produced it, since a reader of the issue has seen neither

## Grounding

- A claim about how an external tool or service behaves carries a
  primary source (official documentation, a man page section, `--help`
  output) or reproduction output that shows it
  - Without either, and for any cause not yet established, state it as
    a hypothesis with the evidence that points to it
- Show the query and the scope behind a negative or absence claim ("no
  X remains")
- Cite source code as a link to its lines at a commit,
  `https://github.com/<owner>/<repo>/blob/<sha>/<path>#L<start>-L<end>`,
  since a bare path and line names neither the repository nor the
  revision, and a link through a branch name points at other lines
  once the branch moves
  - Take the full SHA from the remote, since a link to a commit that
    was never pushed does not resolve: after
    `git -C <clone> fetch origin`, from
    `git -C <clone> rev-parse origin/HEAD`, or with no clone, or when
    `origin/HEAD` does not resolve, from
    `gh api repos/<owner>/<repo>/commits/HEAD --jq .sha`
    - For code that only another branch or a tag holds, put
      `origin/<branch>` or `<tag>^{commit}` in place of `origin/HEAD`,
      and the branch or tag name in place of `HEAD` in the API path
  - Read the line numbers from the file at that SHA, as
    `git -C <clone> grep -n <pattern> <sha> -- <path>` prints them,
    since the working tree may differ from it
  - For a Markdown file put `?plain=1` before `#L`, since line anchors
    apply to the unrendered view
  - GitHub renders such a link as a code snippet only in the repository
    the code is in, so cite code of any other repository as a link
    whose text names the repository, the path, and the lines
- Check that every URL the writer can open resolves to the content it
  is cited for
- Summarize context that lives elsewhere (another issue, a PR, a design
  document) under its link, in the shortest form that survives the link
  going dead

## Form

- The title is a one-line summary of the problem or request, and issue
  references and other detail go in the body
- The language follows the target repository's own rule when it states
  one, otherwise English for an open-source repository, otherwise its
  existing issues
- Write each paragraph and each list item as a single line, with a
  blank line between paragraphs, since GitHub renders a line break
  inside an issue body as a visible break
- Put one claim in each list item, and nest what supports a claim under
  it
- Give each table a lead-in saying what it shows
