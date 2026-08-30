# Implementation Delegation

When to hand implementation work to the `implementer` subagent instead
of implementing in the main session.

## Trigger

- When an approved plan exists, or the user approves a concrete change
  set, delegate the implementation to the `implementer` subagent by
  default
- This applies equally to direct-spec tasks that never went through
  plan mode

## Exceptions (implement inline)

- A one-shot edit of a few lines
- Work that needs the parent's live conversation context and would be
  lossy to re-brief
- Exploratory scope or undecided design (belongs in the parent session
  or a Plan agent first)

Once the decision is to delegate, the git-workflow skill carries the
dispatch procedure, from branch setup through review of the returned
work.
