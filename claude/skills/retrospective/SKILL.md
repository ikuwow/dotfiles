---
description: Use when the user wants to reflect on AI communication quality and get improvement suggestions for rule files or the project itself. TRIGGER when user invokes /retrospective or asks to review the session.
---

# Session Retrospective

Review the current session and identify problematic AI behaviors with
structural countermeasures.

Focus on the interaction process, not on the task content itself.

## Step 1: List Problem Behaviors

Scan the session for AI behaviors that caused issues. For each one, write:

- What the AI did (concrete action, not vague description)
- Why it was a problem (wasted time, wrong output, user had to correct, etc.)

Keep each entry to 1-2 lines. Skip behaviors that had no real impact.

## Step 2: Propose Structural Countermeasures

For each problem behavior, propose a countermeasure that prevents
recurrence through external mechanisms:

- Rule addition (to AIRULES.md for global, or project CLAUDE.md for project-specific)
- Hook (pre-commit, Claude Code PreToolUse/PostToolUse/PermissionRequest hook)
- Linter or static analysis rule
- Script or automation
- Template or checklist
- Permission setting
- Project structure change

Format as a numbered list of pairs. Include a severity rating for each:

```
## 1. <short title>

Problem: <what happened>
Severity: high / medium / low (with brief justification: time wasted, user intervention needed, etc.)
Countermeasure: <structural fix> (scope: global / project-specific)
```

## Prohibited Countermeasures

The following are NOT valid countermeasures. Never propose them:

- "Follow existing rules more carefully" or any variation of rule compliance
- "Pay more attention to X"
- "Be more careful about Y"
- "Remember to Z"
- Any countermeasure that relies on the model's judgment, attention, or
  memory improving in the future
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
