# Subagent Delegation

When delegating work to subagents via the Agent tool:

- Write delegation briefs goal-first: state the outcome and
  constraints, not step-by-step procedures
- Carry the task's depth ceiling into the brief as an explicit stop
  condition (a file count, a number of checks), so the subagent applies
  the same bound the session does
- Answer directly what the session's own loaded context already covers
  (CLAUDE.md, rules, files already read), so a subagent does not pay to
  re-read what the session holds

Do not set the `CLAUDE_CODE_SUBAGENT_MODEL` env var (it overrides
per-invocation model parameters).
