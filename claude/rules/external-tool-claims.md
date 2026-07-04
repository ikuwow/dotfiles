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
