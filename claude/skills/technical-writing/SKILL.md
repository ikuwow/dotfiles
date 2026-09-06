---
name: technical-writing
description: Standards for technical prose - paragraph structure, argument rigor (a mechanism for every causal claim, conditional guarantees, a claim narrowed to what its examples support), reader load, voice, restraint, hollow phrasing, redundancy and where compression stops, and headings. ALWAYS use this skill before writing or rewriting any prose longer than a sentence, even when the request looks like a one-step task you could answer directly: PR bodies, issue bodies and comments, design docs, ADRs, RFCs, README and documentation sections, code review comments, commit message bodies, postmortems, and status updates. Use it when the request only says "write the PR body", "draft the ADR", "summarize this in the issue", or "explain this in the README". Use it whenever the user asks to tighten, shorten, expand, restructure, proofread, edit, or fix prose, or says the writing is too verbose, too dense, or unclear. Use it when reviewing or critiquing someone else's writing. Read japanese.md as well when the text is Japanese.
---

# Technical Writing

Standards for prose in technical documents. Apply them while drafting,
then read the draft once more against Rigor and Compression, which catch
what drafting misses.

For a document written in Japanese, read
[japanese.md](japanese.md) as well. It is written in Japanese and
carries the rules that apply only to Japanese text.

## Scope

These rules govern how prose is built. They do not decide what content a
document carries, how it is marked up, which claims need evidence, or
whether a sentence is grammatical. Where a project rule or another skill
decides one of those, it governs.

Punctuation within a sentence is part of how prose is built, so
[japanese.md](japanese.md) rules on it for Japanese. Markup around the
prose, such as emphasis, headings levels, and line breaks, is not.

Quoted material is outside these rules: a command transcript, a log
excerpt, a diff, and a passage quoted from another document are evidence,
and trimming one to the lines that bear on the argument destroys what
makes it evidence.

## Argument structure

Build the text one paragraph per question the argument answers, so a
reader can follow the reasoning paragraph by paragraph.

- Give each paragraph one topic. Where the paragraph's steps answer one
  question, they are one paragraph however many steps there are; where
  each step would survive on its own, they are that many paragraphs
- Open each paragraph with the sentence that says what the paragraph is
  about
- Where a paragraph's relation to the previous one is not already plain,
  name it in the opening words (therefore, in fact, however)
- Introduce a new term by naming what it applies to, then what it does
  or what it changes, and give the definition after that. A definition
  offered first has nothing for the reader to attach it to
- Run the argument in one direction. State the conclusion once, after
  the objections it rests on are handled, so the reader never meets it
  twice with different support
  - Where the document's own guidelines put the conclusion first, it
    goes first and is not restated once the objections are handled
- Where the text rejects a reading or an alternative, give the reason it
  fails in the same place, and put the rejected design in the
  conditional. An unbuilt alternative in the present tense reads as a
  description of what shipped
- Write out the proposition being denied in the words it would be stated
  in, rather than a vague denial such as "this does not solve
  everything"
- Grant a point you will later qualify by attributing it to whoever
  holds it, so the later correction does not contradict your own earlier
  claim
- Name the knowledge the document assumes its reader already has, since
  an author holding the whole problem leaves prerequisites unstated
- In a list, put the claims at the top level and nest what supports or
  qualifies a claim under it, so the list reads from its top-level lines
  alone

## Rigor

After drafting, read the text once as the objecting reader and check
these.

- State the mechanism behind a causal claim in one sentence: what is
  shared, what propagates, what blocks. Asserting that A leads to B
  leaves the reader unable to check it
- Keep separate decisions, separate causes, and separate kinds of
  problem under separate names
- Where an event has several causes, name each, and say which claim
  accounts for which
- State detection, guarantee, and resolution claims with the condition
  under which they hold: "holds when X", "usually", "makes X more
  likely"
- Check that the examples support the whole claim. Where they support
  part of it, narrow the claim to what they support
- Keep one classification per concept across the whole document, since a
  concept that changes class between sections leaves the reader unable to
  tell whether two passages are about the same thing. Something called a
  human decision in one section is not called a team agreement in another
- Define a term, and the range of things it covers, before the section
  that turns on it
- Before naming several things with one superordinate term, state in one
  sentence what makes them the same thing
- After a concession or a qualification, carry the argument forward.
  Ending on the qualifier leaves the reader without the point
- Anchor every time reference to an event the document names, such as
  the change it describes or a release. "Currently", "new", "as of this
  writing", and "soon" anchored to nothing expire without anyone
  noticing, and a design document is read months later
- Where the text states a count, the list that follows carries that many
  items, and anything outside the counted set says that it is outside

## Reader load

Treat the reader's memory as a budget. Every name and every example the
text introduces has to be worth holding.

- Drop a proper name the text never refers to again, and use the general
  description instead
  - An identifier a reader follows to check a claim stays, since it is
    the claim's provenance
- Where an abstract phrase has more than one possible referent, fix it in
  place with a parenthetical gloss rather than making the reader look
  back
- When adding a second example, say first what it differs in and why one
  was not enough
- Cut detail that does not bear on the section's question, such as
  timestamps, status codes, and decorative precision, and keep the
  specifics the argument needs
- Keep the cells of one table column the same kind of thing, since a
  column the reader cannot predict has to be read row by row
- Give each table a caption or a one-line lead-in saying what it shows,
  so a reader who skips the surrounding prose still knows what they are
  looking at

## Voice

- Write an action with its actor as the subject, so the reader can tell
  who did what. This binds hardest on a claim that something was
  checked, where the actor is what the reader is judging
- Name the specific thing rather than a wide word such as "AI" or "the
  tool"
- Once the text introduces a term, keep using that term. Falling back to
  a vague one later costs the reader the distinction the term made
- Use the plain word where a term-sounding one would carry weight it
  does not have here

## Restraint

Rhetoric is allowed where it does work.

- Write the claim itself instead of announcing that a claim is coming
- State the finding directly instead of building up to it. Keep a
  rhetorical question only where the tension is part of the argument
- State a risk once with the condition under which it occurs, rather
  than listing the consequences that would follow
- Use the plain verb. A metaphor whose referent a reader cannot pin down
  is a defect, not style

## Hollow phrasing

Delete a phrase that adds no point and only signals effort. The families
are announcements and wrap-ups ("it is important to note", "in this
section we will explore"), stance declarations ("tackle head-on"),
hollow adjectives ("essential", "fundamental", "comprehensive"), hollow
verbs ("delve into", "unpack"), connective filler ("in terms of", "from
the perspective of", stacked "furthermore"), and empty intensifiers
("extremely", "highly").

Keep the same word where it carries a claim. The defect is the empty
use, not the vocabulary.

## Compression

Compress until removing anything more would remove one of these: the
mechanism behind a claim, the reason a negation holds, or the bound on a
claim's scope.

- Leave out the intermediate steps a reader supplies without help
- Where several sentences of argument compress into one, or where naming
  the structure conveys it, keep the compressed sentence and leave the
  derivation out
- Where two sections make the same point from different angles, merge
  them. The duplication is in their roles, not their sentences
- After showing something, add only the sentence that says what it
  means. Do not restate what was just shown
- Cut a sentence that only connects or only evaluates, such as "this is
  a good thing in itself"
- Write the claim directly instead of staging a question and answering
  it, and make a concession in your own prose rather than by acting out
  the reader's reaction
  - A question the reader actually has may stay in question form
- State the fact and leave out the positioning around it, such as "this
  document does not dispute that"
- A connective that carries the move from one claim to the next is not
  redundancy

## Headings

- Make a heading name the question the section answers or the object it
  treats. A heading that only names a step, such as "back to the
  example", tells the reader nothing
- Give a heading one phrase naming one thing, rather than a category and
  a subject joined by a dash or a rule
- Keep a section inside what its heading names. Material the heading does
  not reach belongs under its own heading, since a reader who trusts the
  heading stops reading at its edge
