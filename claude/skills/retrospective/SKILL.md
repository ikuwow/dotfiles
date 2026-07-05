---
name: retrospective
description: Use when the user wants to reflect on AI communication quality and get improvement suggestions for rule files or the project itself. TRIGGER when user invokes /retrospective or asks to review the session.
effort: xhigh
---

# Session Retrospective

Review the current session and identify problematic AI behaviors with
structural countermeasures.

Focus on the interaction process, not on the task content itself.

## Step 0: Load Past Retrospectives

Fetch recent retrospective records before analyzing:
`gh issue list --repo ikuwow/dotfiles --label retrospective --state all --limit 15 --json number,title,body,state`
Use them to detect cross-session recurrence: mark any problem that
matches a past retrospective as "recurring" and cite the past issue
number. The severity impact of recurrence is applied once, in the
Severity Criteria adjustment rules below — do not also apply it here.

## Step 1: List Problem Behaviors

Scan the session for AI behaviors that caused issues. For each one, write:

- What the AI did (concrete action, not vague description)
- Why it was a problem (wasted time, wrong output, user had to correct, etc.)

Keep each entry to 1-2 lines. Skip behaviors that had no real impact.

## Step 2: Propose Structural Countermeasures

For each problem, identify the governing rule first, then pick the
highest applicable countermeasure in this order:

1. Fix the existing rule that failed to prevent the behavior.
   Diagnose why it failed — wording too vague, wrong loading tier
   (not in context when needed), or no enforcement — and propose
   editing, splitting, relocating, or mechanizing that rule.
   Never add a parallel rule next to a failed one.
2. Delete or merge rules when overlap, contradiction, or sheer
   volume contributed to the failure.
3. Mechanize (hook, CI check, pre-commit, script, permission
   setting, template) when the behavior is mechanically checkable.
   A mechanized check may replace the prose rule it enforces.
4. Add a new rule only when no existing rule covers the problem.
   State the net context cost: lines added, target loading tier
   (always-loaded rule vs on-demand skill), and what compensating
   trim keeps the tier within budget.

Format as a numbered list of pairs. Include a severity rating for each:

```
## 1. <short title>

Problem: <what happened>
Severity: high / medium / low (with brief justification: time wasted, user intervention needed, etc.)
Countermeasure: <structural fix> (scope: global / project-specific)
```

### Severity Criteria

Judge severity by how disproportionate the burden on the user was
relative to the task's inherent complexity. Evaluate the final outcome,
not intermediate trial-and-error — failed attempts that the AI
self-corrects are not penalized.

| Level | Conditions (any one is sufficient) |
|---|---|
| high | Misjudgment that caused a direction change / User had to redo work manually / Errors introduced into deliverables / Confidently wrong assertion that misled the user |
| medium | User correction or course adjustment needed / Disproportionately many confirmations relative to task complexity / Communication or judgment mistakes that could affect deliverable quality / Silent failure: appeared to succeed but the result was subtly wrong |
| low | AI resolved the issue autonomously without user intervention — including trial-and-error, rule violations caught by hooks, and short-time self-corrections / Minor inefficiency only |

Adjustment rules:

- Within-session recurrence alone does not change severity; a
  self-corrected issue stays at low even when the pattern repeats
  a few times in the session.
- Cross-session recurrence (the same pattern appears in a past
  retrospective issue) escalates one level.
- Excessive recurrence within a session that visibly degrades overall
  response quality can warrant medium, even when each instance is
  self-corrected.
- If high interaction volume is justified by inherent task complexity,
  do not rate it as medium.
- When a checkpoint (plan-mode review, PR review, hook rejection) catches
  an issue, judge severity by the impact the mistake would have had if
  shipped, not by the fact that a checkpoint caught it. Cosmetic or
  "could be cleaned up post-merge" issues stay low even when user
  correction was visible; functionally broken or risky proposals warrant
  medium even when caught early.

### Countermeasure Specificity

Each countermeasure must specify:

- The exact target file path (e.g., `AIRULES.md`, `CLAUDE.md`,
  `.claude/rules/foo.md`, `.pre-commit-config.yaml`)
- The concrete content to add or modify — draft the actual wording, not
  just "add a rule about X"

### Placement Scope

Choose the placement based on who benefits:

- Team-shared enforcement → project's `CLAUDE.md` or its `rules/` directory
- Personal habits or preferences → global `AIRULES.md` or `~/.claude/rules/`
- Memory is for recording facts only. It must not be used as a mechanism
  for behavior change (see Prohibited Countermeasures below).

## Prohibited Countermeasures

The following are NOT valid countermeasures. Never propose them:

- "Follow existing rules more carefully" or any variation of rule compliance
- "Pay more attention to X"
- "Be more careful about Y"
- "Remember to Z"
- Any countermeasure that relies on the model's judgment, attention, or
  memory improving in the future
- "Save to memory" / "Record in memory" — memory depends on model
  judgment for recall and is not a structural enforcement mechanism.
  Memory is valid for recording facts, but not for driving behavior change.
- Restating an existing rule as if adding it would help

The premise: the model's behavior cannot be trusted to improve through
willpower. Only external enforcement mechanisms count.

## Prohibited Root Causes

Do not attribute problems to:

- "Existing rule was not followed" — the rule exists but failed to prevent
  the behavior, so the rule or enforcement is insufficient
- "AI didn't understand the instruction" — if the instruction was clear,
  the question is why the structure allowed misinterpretation

Instead, ask: what structural change would have made the wrong behavior
impossible or caught it before it caused damage?

## Output Format

Keep the output compact. No preamble, no summary section, no closing
remarks. Just the list of problem-countermeasure pairs.

If there are no significant problem behaviors in the session, say so in
one line and stop.

## Step 3: Record the Retrospective

Skip when there were no significant findings. Otherwise create one
GitHub issue in ikuwow/dotfiles holding the problem/countermeasure
list verbatim, via `--body-file` (never `--body`), title
`Retrospective: <date> <one-line session summary>`, label
`retrospective`. The label is provisioned once at setup; if
`gh issue create` fails because it is missing, run
`gh label create retrospective --repo ikuwow/dotfiles --force` and retry.
The weekly-improvement routine consumes these issues — do not
implement the countermeasures in this session unless the user asks.
