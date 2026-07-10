---
name: retrospective
description: Use when the user wants to reflect on AI communication quality and get improvement suggestions for rule files or the project itself. TRIGGER when user invokes /retrospective or asks to review the session.
---

# Session Retrospective

Main session produces first-pass findings from in-memory context, a
Fable subagent (stronger reasoning, session-independent perspective)
reviews them against spot-checked transcript slices, then main routes
the finalized findings.

The Fable subagent runs via the Agent tool's `model:` override, which
works in Claude Code v2.1.202. Do not rely on this SKILL.md's own
frontmatter `model:` field — at this version it does not switch the
orchestrator model, so the orchestrator stays on the session default
and only the delegated subagent gets Fable.

## Step 0: Load past retrospectives

```
gh issue list --repo ikuwow/dotfiles --label retrospective --state all --limit 15 --json number,title,body,state
```

Keep the JSON output for Step 1.

## Step 1: Main first-pass analysis

Read `${CLAUDE_SKILL_DIR}/analysis.md` and follow it to produce
initial findings from the current session's in-memory context — do
not read the transcript file for this step. Substitute the Step 0
JSON output for `<PAST_RETROSPECTIVES>` where analysis.md's
cross-session recurrence check needs it (or the literal string `[]`
if Step 0 returned no issues).

Alongside the findings, produce a factual digest of what the analysis
drew on:

- User-turn references: a paraphrase (not a verbatim quote) of each
  user turn that informed a finding
- Hook / Stop events: any hook rejection, permission denial, or
  Stop-hook trigger observed in the session
- Decisions consulted: plan approvals, explicit user confirmations, or
  routing choices referenced by a finding
- Tool calls: any tool call whose result produced signal for a
  finding, named by command, not full output

The digest is what Fable uses in Step 2 to spot-check coverage — keep
each item specific enough that Fable can verify it against a
transcript slice.

## Step 2: Fable review

Compute the current session's transcript path. The Session ID is
already substituted below when this SKILL.md loads:

- Session ID: `${CLAUDE_SESSION_ID}`
- Munged cwd: run `pwd | tr '/' '-'` (every `/` becomes `-`, so a
  leading `/` becomes a leading `-`)
- Full path: `$HOME/.claude/projects/<munged-cwd>/<session-id>.jsonl`

Confirm the file exists with `ls -la <full-path>` before spawning.
If it does not exist (rare, e.g. the transcript is still buffered),
fall back to the newest `*.jsonl` in `$HOME/.claude/projects/<munged-cwd>/`.

Invoke the Agent tool with:

- `subagent_type`: `general-purpose`
- `model`: `fable`
- `description`: `retrospective review`
- `prompt`: paste the template below, substituting `<TRANSCRIPT_PATH>`
  with the resolved absolute path, `<FINDINGS>` with Step 1's
  findings, and `<DIGEST>` with Step 1's factual digest

Prompt template:

```
You are reviewing a session retrospective's first-pass findings from
the outside.

Instructions: Read the analysis instructions at
${CLAUDE_SKILL_DIR}/analysis.md — they define the severity, taxonomy,
and output format for both the first pass and this review.

Inputs:
- Initial findings (produced by the main session from in-memory context): <FINDINGS>
- Factual digest (what the main session drew on to produce the findings): <DIGEST>
- Session transcript (jsonl, one JSON object per line): <TRANSCRIPT_PATH>

Mandatory: before returning verdicts, sample the transcript with `jq`
/ `grep` regardless of digest quality — around 5-10 slices, under
~20 KB total. Pick slices that let you check digest coverage: a few
user turns, a few tool-call sequences, one or two hook/stop events. Do
not read the whole transcript.

For each initial finding, return one of these verdicts:
- confirm — the finding and the digest line up with the sampled transcript; keep as-is
- adjust — the finding is directionally right but severity, scope, destination, or countermeasure needs a change; state the change
- reject — the finding is not supported by the sampled transcript or the digest misrepresents what happened; state why

Format each verdict as:

## <finding number/title>
Verdict: confirm / adjust / reject
Reason: <one line>
Adjusted finding: <only when Verdict is adjust — state the corrected fields>

If the mandatory slice sample reveals a behavior the digest omitted,
list it separately as a proposed addition, using analysis.md's finding
format plus a Reason line citing the transcript evidence:

## Add missing: <short title>
Problem: <what happened>
Severity: high / medium / low
Scope: global / project-specific
Destination: existing-rule-edit / existing-skill-update / mechanize / new-rule / new-skill
Countermeasure: <structural fix>
Reason: <transcript evidence for this addition>

Do not read the whole transcript. Do not invoke AskUserQuestion or gh
— the orchestrator handles both. Do not add preamble or closing
remarks.
```

## Step 3: Apply verdicts + delta round 2

Apply each Step 2 verdict to its finding:
- confirm — keep the finding as-is
- reject — drop the finding
- adjust — replace the finding with Fable's adjusted version

When main disagrees with a reject or adjust and keeps a version
closer to its own Step 1 finding, record Fable's dissent (its verdict
and reason) alongside the kept finding — Step 4's AskUserQuestion
surfaces both versions so the user arbitrates.

If Step 2 returned any "Add missing" proposals, send a delta-only
round 2 to the same Fable subagent via SendMessage, asking it to
defend each addition with concrete transcript evidence. Do not re-run
the Step 1 findings in round 2 — only the delta.

Round 2 prompt template:

```
Defend the "Add missing" findings from your previous review with
concrete transcript evidence.

Additions to defend: <ADD_MISSING_FINDINGS>

For each addition, cite the specific evidence that supports it — a
line range, the jq/grep query used, or a short quoted snippet. If you
cannot produce concrete evidence for an addition, withdraw it.

Format each response as:

## <addition title>
Evidence: <line range / query / quoted snippet, or "withdrawn">
```

Accept or reject each defended addition based on the evidence
quality. Surface dissent the same way as above when main rejects a
defended addition it disagrees with.

This round is the last one — 2 total Fable rounds is the hard cap.

The finalized findings (Step 1 confirmed/adjusted, plus any accepted
additions, each carrying dissent where present) move to Step 4.

## Step 4: Route findings by scope

Take the finalized findings from Step 3. Each finding carries a
`Scope` (`global` / `project-specific`) tag and a `Destination`
(`existing-rule-edit` / `existing-skill-update` / `mechanize` /
`new-rule` / `new-skill`) tag — originally set in Step 1 and possibly
adjusted in Steps 2-3. Ask the user how to route each finding — do
not auto-file or auto-apply anything. Where a finding carries recorded
Fable dissent (main kept a version Fable rejected or adjusted), show
both versions in the AskUserQuestion so the user arbitrates.

### Sanitize global findings before filing as an issue

This applies only when a global-scope finding is being filed as an
issue below. ikuwow/dotfiles is a public repository: do not include
the names of private repositories, their PR/issue numbers, their
code, or quoted text from their rule files. Describe each problem by
its behavior pattern (e.g., "a work project's Terraform PR review")
so the countermeasure stays understandable without the private
context.

### Ask the user how to route each finding

For each finding, ask via AskUserQuestion using the choices below.

- Project-specific finding: `apply now` / `create issue` / `skip` / `Other`
- Global finding: `create issue` / `skip` / `Other` — no `apply now`
  - The weekly-improvement routine consumes global issues, so
    silently applying them here would skip that queue
  - Editing dotfiles-managed files from an arbitrary project
    session would bypass the dotfiles branch/PR workflow
  - When the session cwd is the dotfiles repo itself, the bypass
    rationale does not hold; keep the ban for consistency and use
    `Other` for a manual dotfiles-side edit

`apply now` branch gate (project-specific only):

- Refuse when HEAD is on the default branch of the current repo,
  detected with the two commands below (both emit the short branch
  name, so a direct string equality holds), and tell the user to
  `create issue` or `skip` instead

```
current=$(git rev-parse --abbrev-ref HEAD)
default=$(git symbolic-ref --short refs/remotes/origin/HEAD | sed 's|^origin/||')
[ "$current" = "$default" ] && refuse
```
- On a feature branch, write files but do NOT commit, then print
  the exact paths written and warn that the changes land in the
  current branch's working tree — commit or discard per the branch's
  PR intent

`apply now` (project-specific only), by destination:

- `existing-rule-edit` / `existing-skill-update` → Edit the target file
- `mechanize` → Write the hook script or CI config; extend
  `.claude/settings.json`'s hooks section if the countermeasure needs
  a new hook entry
- `new-rule` → Write the new rule file; add a 1-line pointer in the
  parent rule if applicable
- `new-skill` → Create the skill directory with a `SKILL.md` skeleton
  and frontmatter; the content is fleshed out in a later session

`create issue`:

- Batch by scope: all approved global findings become one issue in
  `ikuwow/dotfiles`, and all approved project findings become one
  issue in the current cwd's repo — never one issue per finding,
  since the weekly-improvement routine and project maintainers
  consume session-level issues
- Global → `ikuwow/dotfiles`, label `retrospective`, via
  `--body-file` (never `--body`), title
  `Retrospective: <date> <one-line session summary>` (sanitized as
  above). The label is provisioned once at setup; if
  `gh issue create` fails because it is missing, run
  `gh label create retrospective --repo ikuwow/dotfiles --force` and
  retry
- Project-specific → the current cwd's repository, via
  `--body-file`, no label
- The issue body lists each included finding with its `Destination:`
  tag and the concrete countermeasure content, so the
  weekly-improvement routine (or the project's own maintainers) can
  act on each item directly

`skip` — drop the finding with no record.

`Other` — follow the user's free-text instruction.

### Prompt fatigue mitigation

- 4 or fewer findings: ask about all of them in a single
  AskUserQuestion call (max 4 questions per call)
- 5 or more findings: keep only `medium` and `high` severity findings
  for AskUserQuestion; auto-`skip` `low` severity findings and
  announce it in one line ("auto-skipped N low-severity findings")
- If the remaining `medium`+`high` findings still exceed 4, split
  them across multiple AskUserQuestion calls of up to 4 questions each
