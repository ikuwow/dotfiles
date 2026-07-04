# Subagent Model Selection

When spawning subagents via the Agent tool, select the model based
on task complexity to balance cost and capability.

Built-in subagent types have their own defaults — do not override
them (Explore defaults to Haiku; Plan inherits the session model).

For general-purpose subagents:

| Task type | `model` parameter |
|---|---|
| Search, file reading, data gathering, formatting | `"sonnet"` |
| Writing code for well-defined, straightforward tasks | `"sonnet"` |
| Architecture decisions, complex reasoning, large-scale code generation | omit (inherit the session model) |

Do not set the `CLAUDE_CODE_SUBAGENT_MODEL` env var (it overrides
per-invocation model parameters). Skills define their own model in
frontmatter and are not affected by this guideline.
