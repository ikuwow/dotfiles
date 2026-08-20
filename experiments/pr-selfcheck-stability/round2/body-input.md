## Purpose

`Decidable` already governs arrangement across a body — inverted pyramid for order, progressive disclosure for what to defer to the end. Neither says anything about arrangement inside a section, so a section can hold a flat run of same-sized peers mixing the change itself with its rationale, its evidence, and mechanical detail, and pass every property. The reader re-derives a hierarchy the writer never encoded.

`AIRULES.md` already carries half the answer — 「箇条書きの項目はなるべく小さく、1項目1文を基本とし、文末に句点を付けない（複数文の場合は子箇条書きに分ける）」, with PR bodies named in its scope. It went unenforced because `/pr-selfcheck` judges a body against the five properties in `pr-guidelines.md`, and that rule was not among them.

## Key changes

- `Decidable` gains two rules: in a bulleted section the top level carries the change or claim itself so the section reads from its top-level lines alone, and an item that supports, qualifies, or follows from another belongs beneath it rather than beside it
  - the second tests the relation between items rather than counting them, so it carries no threshold; a section whose items really are all independent is a signal about the diff, which `Scoped` already owns
  - counting leaves `Necessary`, whose bullet rule now keeps only distinctness, so one defect no longer draws a finding under two properties
- `pr-guidelines.md` is reformatted to satisfy the rule it now states, converting its rule bullets to a one-sentence top line with their qualifications nested beneath, and lifting onto that line the requirements that sat behind a thesis sentence
  - the file held 45 top-level bullets and nested none of them, the largest flat list among the 17 markdown files under `claude/rules/` and `claude/skills/` at the merge base
    - counted per file with `grep -c '^- '` and `grep -c '^ \+- '` over `git ls-tree -r --name-only main -- claude/rules claude/skills`
- Findings carry one of two severities, `Fix` and `Note`, severed by whether acting on them is required before the PR is ready rather than by whether a statement is true
  - three tiers stood behind two behaviours, since the git workflow acted on Must Fix and Should Fix identically, and the escalation rule that turned two minor findings into a blocker goes with them
  - `Fix` reaches a claim the change rests on, so a missing citation on a passing remark no longer blocks alongside one under the load-bearing claim
  - `Note` is where the call belongs to the reader rather than the checker, which covers a blemish and equally a finding the checker is not confident about
- Three rules that licensed unbounded prose are bounded: a rejected alternative is named when a reviewer would arrive at it and ask, `Scoped` judges whether a hunk sits inside the stated intent, and `Grounded`'s derivation rule reaches a value the reader relies on to stop checking rather than one that only describes the change
  - "Approaches rejected" accepted any contrast, and "leaves no unexplained hunks" reads as an obligation to give every hunk its own item, which is where a flat run of same-weight bullets comes from
- `pr-selfcheck/SKILL.md`'s hard-wrap parser stops matching nested list items, which it would otherwise flag throughout every body now that nesting is the required shape

## Where a reformat can change a rule

Splitting a sentence can change what a rule requires while every clause survives, so a clause-level check passes and the policy still moves. Two rules in `Grounded` sit on that edge and are each verified against `main` separately.

- The evidence rule turns on whether "counting any code block or sub-bullet attached to it" reads as widening what counts as evidence or as a condition restricting where it may sit
  - the inclusive sense is the one `main` carries and the one kept here, so the inline `- [x] <command> → <output>` form the file's own template prescribes stays valid
- The primary-source requirement for external-tool behavior turns on whether it stands alone or qualifies the rule about URLs justifying configuration values
  - it fires on any claim about a tool this diff does not modify, so it is a `Grounded` rule in its own right rather than a child of the configuration-value rule

## Verification

- [x] Clause mapping built against `git show main:claude/skills/git-workflow/pr-guidelines.md`, covering the 37 rule bullets the reformat carried over, with every clause landing at exactly one destination and none dropped or duplicated
  - the rules this branch adds are new text rather than carried-over clauses, so they are outside what the mapping checks
  - wording changes are confined to splitting at sentence boundaries, dropping the trailing period, and promoting a trailing subordinate clause to an independent sentence
  - the record is at `ikuwowfiles/pr-guidelines-reformat-check.md`, gitignored, so it is checkable on the authoring machine but not from a clone
- [x] The two restored rules carry the same requirement they carry at `main`, checked by diffing each against `git show main:claude/skills/git-workflow/pr-guidelines.md`
- [x] The five property definitions and the PR Body Template block survive untouched → `diff` of the header property list and of the template block against `main` both exit 0
- [x] Every rule in the five property sections is present at the top level, not only in a child, checked by reading each section with its sub-bullets filtered out
- [x] No rule belongs to two properties → grouping and nesting appear only under `Decidable`, distinctness and non-restatement only under `Necessary`, and no rule in either counts bullets
