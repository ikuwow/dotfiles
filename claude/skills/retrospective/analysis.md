# Retrospective analysis instructions

## Reader context

This file has two consumers: the main session, which applies it to
in-memory session context during the first pass, and a Fable
subagent, which applies it to spot-checked transcript slices during
review.

Analyze the session's interaction record — in-memory session context
for the main first pass, sampled transcript slices for the Fable
review — and past retrospective issues, then produce a list of
problem behaviors with structural countermeasures.

Focus on the interaction process, not on the task content itself.

## Cross-session recurrence

Mark any problem that matches a past retrospective as "recurring" and
cite the past issue number. The severity impact of recurrence is
applied once, in the Severity Criteria adjustment rules below — do not
also apply it here.

## Step 1: List problem behaviors

Scan the session for AI behaviors that caused issues. For each one, write:

- What the AI did (concrete action, not vague description)
- Why it was a problem (wasted time, wrong output, user had to correct, etc.)

Keep each entry to 1-2 lines. Skip behaviors that had no real impact.

## Step 2: Propose structural countermeasures

For each problem, identify the governing rule first, then pick the
highest applicable destination in this order:

1. `existing-rule-edit` — an existing rule failed to prevent the behavior (vague wording, wrong loading tier, or no enforcement); edit, split, relocate, or mechanize it, never add a parallel rule next to a failed one
1. `existing-skill-update` — an existing skill file (`SKILL.md`, `analysis.md`, etc.) failed to guide the behavior; edit it directly
1. `mechanize` — the behavior is mechanically checkable; add a hook, CI check, pre-commit, script, permission setting, or template, which may replace the prose rule it enforces
1. `new-rule` — no existing rule covers the problem; state the net context cost (lines added, target loading tier, compensating trim)
1. `new-skill` — no existing skill covers the problem and it needs a new on-demand workflow; scaffold a new skill

A countermeasure that deletes or merges existing rules or skills is an
orthogonal edit operation, not a destination of its own — apply it
alongside whichever destination above the finding routes to, when
overlap, contradiction, or sheer volume contributed to the failure.

Format as a numbered list of pairs. Include a severity rating, a
scope tag (global / project-specific), and a destination tag for each:

```
## 1. <short title>

Problem: <what happened>
Severity: high / medium / low (with brief justification)
Scope: global / project-specific
Destination: existing-rule-edit / existing-skill-update / mechanize / new-rule / new-skill
Countermeasure: <structural fix>
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

### Placement Scope (used for the Scope tag)

Choose the placement based on who benefits:

- Team-shared enforcement → project's `CLAUDE.md` or its `rules/` directory (tag: project-specific)
- Personal habits or preferences → global `AIRULES.md` or `~/.claude/rules/` (tag: global)
- Memory is for recording facts only. It must not be used as a mechanism
  for behavior change (see Prohibited Countermeasures below).
- Choose placement by scope only. When the scope-correct file is at
  its line budget, propose raising the budget or trimming that file —
  never relocate the rule to a different tier to fit the budget

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
remarks. Just the list of problem-countermeasure pairs, each tagged
with severity and scope.

If there are no significant problem behaviors in the session, say so in
one line and stop.

## Reading the transcript

This section applies to Fable during Step 2; the main session does
not read the transcript in Step 1.

The jsonl is one JSON object per line and can be large (hundreds of
KB to several MB) with verbose noise — full tool outputs, injected
CLAUDE.md / system-reminder blocks, permission prompts. Do not read
the whole file, regardless of size — always slice-sample.

- Use Bash (`wc -l`, `jq`, `grep`, `tail`) to extract targeted slices
  covering user turns, the assistant's own text and reasoning, tool
  calls and their key results, and hook / Stop events
- Skip or skim bulk tool output and repeated system reminders
- The transcript may not include the currently-in-progress turn (the
  one that triggered this retrospective); when the digest describes
  behavior from that turn but the sampled slices do not confirm it,
  return `unverifiable` for that finding rather than `reject` — see
  the verdict schema in SKILL.md's Step 2
