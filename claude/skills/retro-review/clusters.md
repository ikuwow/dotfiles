# Failure-Mechanism Cluster Taxonomy

Starting taxonomy for retro-review clustering, established in the
2026-07 pilot analysis. It is revisable: clusters may be added, split,
or merged when a cycle's data demands it — record such changes in that
cycle's report.md.

## Clusters

- M1 external-unverified — asserted or relied on external tool/system
  behavior or interfaces without consulting a primary source (docs,
  man, --help, source code, measurement); includes interface analogy
  misuse (e.g. jq flags applied to yq)
- M2 rule-application-gap — a rule, approved plan, or in-session
  lesson was present in context but not consulted at the moment of
  action; subtypes: (a) meta-conventions of the artifact being written
  not applied before writing, (b) habitual operation overriding a
  known rule, (c) plan constraints not re-read at execution time,
  (d) a lesson from a previous subtask not carried into the next
- M3 size-based-skip — a size-independent procedure (branching,
  delegation, advisor, workflow) skipped because the task looked small
  or casual
- M4 overclaim — persisted artifacts or reports claiming stronger or
  more quantitative verification than was actually performed
- M5 hedge-substitute — an "unverified" label, a question to the user,
  or a skipped advisor call used in place of a cheap verification the
  agent could have run itself
- M6 partial-verification — whole-goal success inferred from a partial
  check or an assumption, without enumerating prerequisites backward
  from the goal
- M7 literal-scope-reading — rule wording read narrowly or literally,
  without deriving the applicable scope from the underlying design
  principle
- M8 user-context-miss — established user patterns, delegation
  signals, or nearby context ignored in favor of generic behavior;
  includes confirm-versus-proceed boundary errors in auto mode
- M9 approval-scope-inflation — plan approval or a broad go-ahead
  interpreted as covering individual externally visible mutations
- M0 misc — genuine one-offs only; keep this small

## Assignment rules

- Every finding gets exactly one primary cluster
- Cluster on the `root` field's mechanism, never on `feedback_target`
- Most specific mechanism wins: M9, M5, M3, M4, M7 are narrow; M1, M2,
  M6, M8 are broad (a hedge-driven verification skip is M5, not M1; a
  size-rationalized branch skip is M3, not M2)
- M1 vs M2 boundary: the unchecked fact needed an external primary
  source → M1; it was already knowable from session context or local
  files → M2
- M3 requires the `root` to explicitly cite size or casualness as the
  reason; otherwise assign the underlying mechanism
