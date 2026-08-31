# Subagent Delegation

When delegating work to subagents via the Agent tool:

- Write delegation briefs goal-first: state the outcome and the
  constraints the conversation settled (branch and PR shape, scope
  limits, what to leave alone), not step-by-step procedures
  - The subagent does not see the conversation, so a constraint left
    out of the brief is one it will not honor
- Carry the task's depth ceiling into the brief as an explicit stop
  condition (a file count, a number of checks), so the subagent applies
  the same bound the session does
- Answer from the session's own loaded context (CLAUDE.md, rules,
  files already read) instead of delegating, so a subagent does not
  pay to re-read what the session holds

Select each subagent's model with the Agent tool's per-invocation
`model` parameter, and leave the `CLAUDE_CODE_SUBAGENT_MODEL` env var
unset (it overrides that parameter).
