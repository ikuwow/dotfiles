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
`global` or `project-specific`. Do not create GitHub issues and do
not invoke AskUserQuestion — the orchestrator handles routing after
you return. Do not add preamble or closing remarks.
```

## Step 2: Route findings by scope

Take the subagent's output verbatim and act on each finding based on
its Scope tag.

### Global-scope findings

ikuwow/dotfiles is a public repository. Before filing, sanitize the
global-scope problem/countermeasure pairs: do not include the names
of private repositories, their PR/issue numbers, their code, or
quoted text from their rule files. Describe each problem by its
behavior pattern (e.g., "a work project's Terraform PR review") so
the countermeasure stays understandable without the private context.

Create one GitHub issue in ikuwow/dotfiles holding the sanitized
pairs via `--body-file` (never `--body`), title
`Retrospective: <date> <one-line session summary>` (sanitized as
above), label `retrospective`. The label is provisioned once at
setup; if `gh issue create` fails because it is missing, run
`gh label create retrospective --repo ikuwow/dotfiles --force` and retry.
Skip issue creation when there are no global-scope findings.

The weekly-improvement routine consumes these issues — do not
implement global countermeasures in this session unless the user asks.

### Project-scope findings

Never file these as retrospective issues in ikuwow/dotfiles. Present
them in the session and ask the user how to handle them
(AskUserQuestion), offering these choices for each finding: apply to
the project's rule files now / create an issue in the project's own
repository / drop.
