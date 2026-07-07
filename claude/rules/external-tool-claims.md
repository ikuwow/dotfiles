# External Tool Behavior Claims

When making recommendations or assertions that depend on the behavior
of an external tool (OS, runtime, cloud service, CLI, library), verify
that behavior against primary sources before stating it.

## When this applies

- Stating how a tool resolves config paths, environment variables, or
  precedence between them
- Stating that a tool persists or regenerates state across operations
  (delete + recreate, restart, version upgrade)
- Stating idempotency, safety, or side-effect properties
- Recommending a workflow that depends on a tool doing something
  reliably under specific conditions
- Stating how Claude Code itself behaves — skill auto-invocation
  triggers, `model:` frontmatter effects, subagent context
  inheritance, hook execution, permission evaluation, and what the
  user actually sees of a turn (tool inputs and Write file contents
  are not rendered to the user) — is exactly as fact-checkable as
  third-party tool behavior, and just as often wrong from unverified
  recall. For which model actually served a turn, the session
  jsonl's `.message.model` is the ground truth; the environment
  identity string ("You are powered by …") is injected branding and
  can disagree with the runtime.

## Verification sources, in priority order

1. Official documentation (project docs site, man page, `--help` output)
2. Source code of the tool itself (`gh search code`, `gh api`,
   `deepwiki`, `context7`)
3. Issues / discussions with reproducible reports

If none of these can be verified, mark the claim as `要検証 / unverified`
and either ask the user to verify with a clear "I have not confirmed
this" caveat, or investigate yourself before asking the user to spend
their time testing it on their host.

## Don't

- Write "〜のはず" / "〜される" without a primary source check
- Ask the user to test something on their host before reading the tool's
  source for the relevant code path
- Treat training-data recall as verification — re-confirm via a primary
  source even when you "know" the answer
- Layer multiple unverified workarounds on top of a tool whose behavior
  was never read; root-cause first by reading the source
- Treat examples or assertions inside local rule/skill files as
  primary sources for external-service behavior — rule prose
  documents policy, not measured fact; measure the API response
  itself
