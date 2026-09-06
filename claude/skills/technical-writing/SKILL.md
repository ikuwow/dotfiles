---
name: technical-writing
description: Standards for technical prose you write or revise - PR bodies, issue bodies, design docs, ADRs, README sections, review comments, and any explanatory text longer than a sentence. Covers paragraph structure, argument rigor (a mechanism for every causal claim, conditional guarantees, hedges that survive editing), reader load, voice, restraint, hollow phrasing, redundancy and where compression stops, and headings. Trigger whenever such text is being drafted or rewritten, including when the request only says "write the PR body", "draft the ADR", or "summarize this in the issue", and whenever the user asks to tighten, expand, restructure, or fix prose. Trigger equally when reviewing someone else's prose for quality.
---

# Technical Writing

Standards for prose in technical documents. Apply them while drafting,
then read the draft once more against the Rigor and Redundancy sections,
which catch what drafting misses.

For a document written in Japanese, read
[japanese.md](japanese.md) as well. It carries the rules that
apply only to Japanese text.

## Scope

These rules govern how prose is built. They do not decide what content a
document carries, how it is formatted, or which claims need evidence.
Where a project rule or another skill decides one of those, it governs.

## Paragraph and argument structure

Build the text one paragraph per step of the argument, so a reader can
follow the reasoning paragraph by paragraph.

- Give each paragraph one topic. A paragraph that moves through
  investigation, finding, and evaluation is that many paragraphs
- Open each paragraph with the sentence that says what the paragraph is
  about
- Where a paragraph's relation to the previous one is not already plain,
  name it in the opening words (therefore, in fact, however)
- Introduce a new term by naming what it applies to, then what it does
  or what it changes, and give the definition after that
- Run the argument in one direction: handle the objections, then state
  the conclusion once at the end
- Where the text rejects a reading or an alternative, give the reason it
  fails in the same place, often as a counterfactual
- Write out the proposition being denied in the words it would be stated
  in, rather than a vague denial such as "this does not solve
  everything"
- Grant a point you will later qualify by attributing it to whoever
  holds it, so the later correction does not contradict your own earlier
  claim
- Name the knowledge the document assumes its reader already has, since
  an author holding the whole problem leaves prerequisites unstated

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
- Keep one classification per concept across the whole document.
  Something called a human decision in one section is not called a team
  agreement in another
- Define a term, and the range of things it covers, before the section
  that turns on it
- Before naming several things with one superordinate term, state in one
  sentence what makes them the same thing
- After a concession or a qualification, carry the argument forward.
  Ending on the qualifier leaves the reader without the point
- Write in terms that stay true as the document ages. "Currently", "now",
  "new", "as of this writing", and "soon" expire without anyone noticing,
  and a design document is read months later

## Reader load

Treat the reader's memory as a budget. Every name and every example the
text introduces has to be worth holding.

- Drop a proper name the text never refers to again, and use the general
  description instead
- Where an abstract phrase has more than one possible referent, fix it in
  place with a parenthetical gloss rather than making the reader look
  back
- When adding a second example, say first what it differs in and why one
  was not enough
- Cut detail that does not bear on the section's question, such as
  timestamps, status codes, and decorative precision, and keep the
  specifics the argument needs

## Voice

- Write an example as actions with the actor as subject, so the reader
  can tell who did what
- Name the specific thing rather than a wide word such as "AI" or "the
  tool"
- Once the text introduces a term, keep using that term. Falling back to
  a vague one later costs the reader the distinction the term made
- Use the plain word where a term-sounding one would carry weight it
  does not have here

## Restraint

Rhetoric is allowed where it does work. These bound where that is.

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

## Redundancy and where compression stops

Compress until removing anything more would remove one of these: the
mechanism behind a claim, the reason a negation holds, an uncertainty
marker, or the bound on a claim's scope.

- Leave out the intermediate steps a reader supplies without help
- Where several sentences of argument compress into one, keep only the
  compressed sentence
- Where two adjacent sections make the same point from different angles,
  merge them. The duplication is in their roles, not their sentences
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
- Where naming the structure conveys it, name it and state the result
  instead of walking the derivation
- A connective that carries the move from one claim to the next is not
  redundancy

## Headings

- Make a heading name the question the section answers or the object it
  treats. A heading that only names a step, such as "back to the
  example", tells the reader nothing
- Give a heading one phrase naming one thing, rather than two elements
  joined by a separator
