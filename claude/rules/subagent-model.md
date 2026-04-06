# Subagent Model Selection

When spawning subagents via the Agent tool, select the model based on task
complexity to balance cost and capability.

## Model Guidelines

Built-in subagent types have their own defaults — do not override them:

- **Explore**: defaults to Haiku (already optimized, no override needed)
- **Plan**: inherits from the main session model (Opus — no override needed)

For **general-purpose** subagents, apply these rules:

| Task type | `model` parameter |
|---|---|
| Search, file reading, data gathering, formatting | `"sonnet"` |
| Writing code for well-defined, straightforward tasks | `"sonnet"` |
| Architecture decisions, complex reasoning, large-scale code generation | omit (inherits Opus) |

## Rationale

- Opus is reserved for tasks that genuinely require deep reasoning.
- `CLAUDE_CODE_SUBAGENT_MODEL` env var is NOT used because it overrides
  per-invocation model parameters and would weaken Plan agents.
- Skills define their own model in frontmatter and are not affected by
  this guideline.
