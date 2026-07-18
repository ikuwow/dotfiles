# Subagent Model Selection

When spawning subagents via the Agent tool, select the model based
on task complexity to balance cost and capability.

Built-in subagent types have their own defaults — do not override
them.

For general-purpose subagents:

| Task type | `model` parameter |
|---|---|
| Search, file reading, data gathering, formatting | `"sonnet"` |
| Writing code for well-defined, straightforward tasks | `"sonnet"` |
| Multi-file implementation, non-trivial investigation, deep debugging, adversarial review | `"opus"` |

Run a subagent on `"fable"` — including by omitting `model` under a
Fable session — only on explicit user instruction; agents and skills
that pin `fable` in their own definition (e.g. fable-advisor) are
exempt.

## Delegation economy

- Delegate independent, fan-out-able subtasks to subagents instead of
  running them inline
- Keep the main session for orchestration, design decisions, and
  final review
- Write delegation briefs goal-first: state the outcome and
  constraints, not step-by-step procedures

Do not set the `CLAUDE_CODE_SUBAGENT_MODEL` env var (it overrides
per-invocation model parameters). Skills define their own model in
frontmatter and are not affected by this guideline.
