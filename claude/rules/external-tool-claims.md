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
  inheritance, hook execution, permission evaluation, or what the
  user actually sees of a turn (e.g., whether tool inputs or Write
  file contents are rendered to the user)

## Verification sources, in priority order

1. Official documentation (project docs site, man page, `--help` output)
2. Source code of the tool itself (`gh search code`, `gh api`,
   `deepwiki`, `context7`)
3. Issues / discussions with reproducible reports

For which model served a turn, prefer the session jsonl's
`.message.model` over the environment identity string ("You are
powered by …"); the two can disagree.

When a primary source could exist but you have not read it, investigate
first (docs / man page / `--help` / source via `gh api ... -H "Accept:
application/vnd.github.raw"` / `deepwiki` / `context7`) before writing
the claim, recommending the tool or service, or asking the user to
test it on their host. Marking the claim `要検証 / unverified` is not
a substitute for that investigation — it is reserved for cases where
the primary source is genuinely unreachable (offline, host-local
state, non-public code) or has been read and remains inconclusive.
Only in those cases may you ask the user to verify, and only with a
clear "I have not confirmed this" caveat.

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
