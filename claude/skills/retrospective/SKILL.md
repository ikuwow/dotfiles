---
name: retrospective
description: Use when the user wants to reflect on AI communication quality and get improvement suggestions for rule files or the project itself. TRIGGER when user invokes /retrospective or asks to review the session.
---

# Session Retrospective

Delegate the transcript analysis to a Fable subagent (stronger
reasoning, session-independent perspective), then route the findings
from the main session.

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

## Step 1: Delegate analysis to a Fable subagent

Compute the current session's transcript path. The Session ID is
already substituted below when this SKILL.md loads:

- Session ID: `${CLAUDE_SESSION_ID}`
- Munged cwd: run `pwd | tr '/' '-'` (every `/` becomes `-`, so a
  leading `/` becomes a leading `-`)
- Full path: `$HOME/.claude/projects/<munged-cwd>/<session-id>.jsonl`

Confirm the file exists with `ls -la <full-path>` before spawning.
If it does not exist (rare, e.g. the transcript is still buffered),
fall back to the newest `*.jsonl` in `$HOME/.claude/projects/<munged-cwd>/`.

Then invoke the Agent tool with:

- `subagent_type`: `general-purpose`
- `model`: `fable`
- `description`: `retrospective analysis`
- `prompt`: paste the template below, substituting `<TRANSCRIPT_PATH>`
  with the resolved absolute path and `<PAST_RETROSPECTIVES>` with the
  JSON output from Step 0 (or the literal string `[]` if empty).

Prompt template:

```
You are performing a session retrospective on the outside.

Instructions: Read the analysis instructions at
${CLAUDE_SKILL_DIR}/analysis.md and follow them exactly.

Inputs:
- Session transcript (jsonl, one JSON object per line): <TRANSCRIPT_PATH>
- Past retrospectives on this project (for cross-session recurrence detection): <PAST_RETROSPECTIVES>

Output: return the analysis findings in the format specified in
analysis.md. For each finding, include a `Scope:` tag with value
`global` or `project-specific`, and a `Destination:` tag with one of
`existing-rule-edit` / `existing-skill-update` / `mechanize` /
`new-rule` / `new-skill`. Do not create GitHub issues and do
not invoke AskUserQuestion — the orchestrator handles routing after
you return. Do not add preamble or closing remarks.
```

## Step 2: Route findings by scope

Take the subagent's output verbatim. Each finding carries a `Scope`
(`global` / `project-specific`) tag and a `Destination`
(`existing-rule-edit` / `existing-skill-update` / `mechanize` /
`new-rule` / `new-skill`) tag from Step 1. Ask the user how to route
each finding — do not auto-file or auto-apply anything.

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
- Global finding: `create issue` / `skip` / `Other` — no `apply now`,
  because the weekly-improvement routine consumes global issues, and
  editing dotfiles-managed files from a project session would bypass
  the dotfiles branch/PR workflow; when the session cwd is the
  dotfiles repo itself the bypass rationale does not hold, but keep
  the ban for consistency and use `Other` for a manual dotfiles-side edit

`apply now` branch gate (project-specific only):

- Refuse when HEAD is on the default branch of the current repo
  (detect via `git symbolic-ref refs/remotes/origin/HEAD` and compare
  to `git rev-parse --abbrev-ref HEAD`), and tell the user to
  `create issue` or `skip` instead
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

`skip`: drop the finding, no record.

`Other`: follow the user's free-text instruction.

### Prompt fatigue mitigation

- 4 or fewer findings: ask about all of them in a single
  AskUserQuestion call (max 4 questions per call)
- 5 or more findings: keep only `medium` and `high` severity findings
  for AskUserQuestion; auto-`skip` `low` severity findings and
  announce it in one line ("auto-skipped N low-severity findings")
- If the remaining `medium`+`high` findings still exceed 4, split
  them across multiple AskUserQuestion calls of up to 4 questions each
