---
name: rule-edit
description: Changing or judging a rule document that an AI agent loads as instructions - CLAUDE.md, AGENTS.md, AIRULES.md, files under .claude/rules/, any file whose consumer is an agent rather than a person. Carries the criteria for what belongs in a rule (振り分け, 採用基準), how to word it (書き方), where to put it (配置), and the procedure - scope, enumerating every existing statement that decides the same question, integrating rather than appending, verifying a compression dropped nothing, and a fresh-context compliance check. Trigger whenever a task will add, reword, delete, compress, split, or relocate an instruction in such a file, including a one-line tweak, a "just add a rule so you stop doing X" request, and rule edits reached from /retro-review or a retrospective. Trigger equally when the user only asks about an existing rule rather than asking for an edit - whether it is worded well, whether it belongs where it sits, whether it duplicates another rule, whether it should be a rule at all or a skill or a hook - since answering that needs the same criteria.
---

# Rule Edit

`criteria.md`, beside this file, is the specification these steps enforce. It
decides what belongs in a rule at all (振り分け), what to keep (採用基準), how
to word it (書き方), and where to put it (配置). Read it before Step 1. The
steps below sequence those criteria and add the checks that only apply while
an edit is being made: the hook pre-emption test, the compression mapping, the
fresh-context review, and what the PR body has to carry.

Run Steps 1 through 3 before writing the edit. They are what keeps one
question from ending up answered in two files, and an edit already written is
an edit already anchored.

## Step 1: Name the scope

Say in the assistant message whether the change is global (every project,
every task) or project-specific. A constraint scoped one level too wide loads
into work it cannot help, and one scoped too narrow stops applying where the
failure recurs. Which file it lands in follows from Step 3, once the mechanism
is settled.

Note which agents a destination reaches, since a move between two of them
narrows or widens who obeys the statement. In `ikuwow/dotfiles`,
`scripts/deploy.sh` gives four classes:

- `AIRULES.md` reaches Claude, Codex, and Junie
- `claude/rules/` reaches Claude alone
- `claude/skills/` reaches Claude and Junie
- `codex/rules/` reaches Codex alone

## Step 2: Enumerate every statement that decides the same question

Search for statements bearing on the question this edit decides, and list them
with file and line number. The search space is whatever the agents in play
actually load, which spans two roots that need different commands:

```
# the target project's own rule documents
git grep -n '<term>\|<synonym>\|<both the English and the Japanese form>' -- <paths>

# the user-level set, whose entries are symlinks, so -R rather than -r
grep -Rn '<the same pattern>' ~/.claude/CLAUDE.md ~/.claude/rules/ ~/.claude/skills/ ~/.claude/agents/
```

`grep -r` skips symlinks it meets during recursion, and every entry under
`~/.claude/rules/` is one, so a lowercase `-r` reports a clean search of
nothing.

Grep on the terms the decision would be worded with, not on the wording you
are about to write, and widen the pattern until it catches statements phrased
differently from yours. A term that only appears in your new wording proves
nothing.

Then read what comes back and classify each hit:

- Decides the same question the same way: this is a duplicate, and the edit
  belongs in whichever copy survives
- Decides the same question differently: this is a contradiction, and which
  one wins is the user's call, not yours
- Decides a neighbouring question: leave it, and say so, so the reader can see
  it was considered

Present the enumeration to the user before writing the edit when it turns up a
contradiction. A rule set where one question has two answers behaves
differently from session to session, which is the failure this step exists to
prevent.

## Step 3: Decide where the statement lands

Route the statement with `criteria.md` 振り分け, which lists the mechanisms and
what each one claims. Read it there rather than from memory: a rule is what
survives after every other mechanism has taken what it claims, so a route this
step skips sends content to the always-loaded set by default.

Check whether a hook already enforces the constraint. In `ikuwow/dotfiles` the
hooks are the scripts under `claude/hooks/` and their wiring in
`claude/settings.json`'s `hooks` section. A hook that already blocks the action
makes a matching rule line a pre-emption rather than a duplicate, so the rule
earns its place by saving a denied tool call; a rule with no such role is text
the hook already covers.

When the routing lands the content in a skill and a rule still has to send the
reader there, leave a trigger pointer in the rule naming the skill. 配置 例外2
allows it, and the pointer is what makes an on-demand mechanism reachable from
a session that has not loaded it. Content that stays a rule needs no pointer:
a rule file without `paths` frontmatter loads unconditionally.

## Step 4: Integrate rather than append

When the change alters how an existing instruction applies, rewrite that
instruction. Appending a qualifier beside it leaves both readings loaded at
once, and the model then picks one per session.

Write the result in the file's own language, in the affirmative form and
one-sentence-per-bullet shape `criteria.md` 書き方 and the AIRULES.md
output-format rules ask for.

## Step 5: Verify a compression dropped nothing

When the edit compresses, simplifies, or splits existing text, build a mapping
from every original bullet to where its instruction now lives, one row per
original bullet. A row with no destination is a policy loss, and it is either
restored or declared.

Two failure modes this catches:

- The surviving statement scopes itself out of the deleted line's case, so the
  mapping looks right while the coverage is absent
  - Read the survivor's own scope sentence, not just its topic
- The survivor covers half the deleted line
  - A line deciding both what to verify and when to stop needs both halves
    rehomed

Put the mapping in the PR body. It is the only place a reviewer can check the
claim, since the surviving statements are outside the diff.

## Step 6: Check compliance from a fresh context

Dispatch a general-purpose subagent on `opus` to check the edited files against
`criteria.md`. Its clean context is what makes the check worth running: the
session that wrote the edit knows what it meant, and reads the intent back into
the words. Name the model rather than inheriting, so the check does not land on
whatever the session happens to be running.

Brief it with the repository path, the branch, the resolved path of
`criteria.md`, and the files to check, and ask for per-file findings against
the whole specification. Give it nothing about why the edit was made, for the
same reason.

`${CLAUDE_SKILL_DIR}` resolves the skill path for a subagent, and it points at
the deployed copy under `$HOME`. When the edit targets the repository that
backs that copy, hand over the in-repo path instead, so the reviewer reads the
same file the branch changes.

Act on what it returns, then re-read the edited file yourself once. The
subagent judges wording against the specification; whether the rule still says
what the user decided is yours to confirm.

## Step 7: State the verification in the PR body

The PR body carries the scope from Step 1, the enumeration from Step 2 with
its command and output, and the mapping from Step 5. Re-run any command whose
output the body quotes, at the wording the branch actually ends with — a
transcript edited by hand to match reworded text stops reproducing, and the
body's evidence is then a claim about a command rather than its result.
