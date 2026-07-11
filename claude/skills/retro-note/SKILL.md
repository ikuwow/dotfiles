---
name: retro-note
description: Use for a lightweight, shallow log of AI-mistake analysis appended to a per-project jsonl file, as a lower-cost alternative to the full /retrospective. TRIGGER automatically when the user declares session completion (per the AIRULES.md rule), or when the user invokes /retro-note directly.
---

# Retro Note

Do not rely on this SKILL.md's own frontmatter `model:` field to switch
models — this skill has none, and the analysis runs on the current
session's own model (no Fable subagent, no delegation). This keeps the
per-session cost low; batch analysis across accumulated notes is a
separate, later skill.

## Purpose

This writes a shallow AI-mistake analysis of the current session to a
project-scoped jsonl file (`~/.claude/retrospective/notes/<project-slug>/YYYY-MM.jsonl`)
for later batch review across sessions. It does not do deep analysis or
interactive routing — for that, `/retrospective` remains available and
should be invoked explicitly when a deep dive is warranted.

## Scope of findings

In scope — AI-side judgment failures only:

- (a) 誤った前提や思い込みで着手したケース
- (b) rule違反や rule趣旨から外れた選択
- (c) tool選択・path選択のミス
- (d) userへの応答の不適切さ（浅い、的外れ、確認不足、押し付け等）
- (e) 情報検証の不足（一次情報を確認せずに断定した等）

Out of scope: session内容の振り返り、成功事例、user側の判断・行動、
外部ツールの不具合。

## Depth requirement

The analysis is shallow but must reach the mechanism level, not just
restate what happened. Both conditions must hold for every finding:

1. Separate `behavior` (the AI's actual, observable action) from
   `root` (why the judgment failed, at the mechanism level — not just
   "what happened" again).
1. `root` must not be a restatement of `behavior`.

Calibration example:

- NG (root restates behavior): "Xを確認せず着手した" → "Xを確認しなかった"
- OK (root reaches mechanism): "Xを確認しなかったのは Y という制約から
  思考を始めたからで、goalからの逆算をスキップした"

## Step 1: Resolve transcript path

Same logic as `/retrospective`. The Session ID is already substituted
below when this SKILL.md loads:

- Session ID: `${CLAUDE_SESSION_ID}`
- Munged cwd: run `pwd | tr '/' '-'` (every `/` becomes `-`, so a
  leading `/` becomes a leading `-`)
- Full path: `$HOME/.claude/projects/<munged-cwd>/<session-id>.jsonl`

Confirm the file exists with `ls -la <full-path>`. If it does not
exist (rare, e.g. the transcript is still buffered), fall back to the
newest `*.jsonl` in `$HOME/.claude/projects/<munged-cwd>/`.

## Step 2: Analyze the in-context conversation

Using the main session's own context (no subagent, no Fable),
identify findings that satisfy both the scope and depth rules above.

- Maximum 5 findings. If more than 5 qualify, keep the 5 highest by
  `severity`.
- Each finding must include:
  - `behavior`: the observable action
  - `root`: the mechanism-level reason, not a restatement of `behavior`
  - `transcript_ref`: either a `turns` array of approximate turn
    indices, or a `lines` array of approximate line ranges in the
    transcript jsonl — pick whichever is easier to determine from
    context
  - `severity`: one of `low` / `medium` / `high`
  - `feedback_target`: a single best-guess AIRULES.md section name,
    rule file, or skill name this finding is likely to cluster under
    (for future batch review — do not decide here whether a rule
    change is warranted)

## Step 3: Determine the project slug

1. If `git -C <cwd> rev-parse --show-toplevel` succeeds, use its
   basename as the slug.
1. Otherwise, use the cwd basename as the slug.
1. If neither resolves, use `unknown`.
1. Sanitize the slug by replacing `[^A-Za-z0-9_-]` with `-`.

Create the directory:

```
mkdir -p ~/.claude/retrospective/notes/<project-slug>
```

## Step 4: Build and append the record

Build one JSON record for the whole session (not one per finding):

```json
{
  "ts": "2026-07-11T10:56:09+09:00",
  "session_id": "abc123",
  "transcript_path": "/Users/ikuwow/.claude/projects/-Users-ikuwow-dotfiles/abc123.jsonl",
  "cwd": "/Users/ikuwow/dotfiles",
  "git_repo_root": "/Users/ikuwow/dotfiles",
  "git_branch": "main",
  "pr_number": null,
  "task_summary": "retrospective仕組みの再設計プランニング",
  "findings": [
    {
      "behavior": "初回プランで SessionEnd hook を軸に設計し、record schemaを transcript_path + cheap metadata のみに決めた",
      "root": "「後段のバッチが何を必要とするか」から逆算せず、hook API の payload と実装容易性という道具側の制約から思考を始めた。goal（バッチ分析が意味を持つ最小情報単位）を最初に定義するステップを飛ばしている",
      "transcript_ref": {"turns": [8, 10]},
      "severity": "medium",
      "feedback_target": "AIRULES.md 応答の姿勢と判断 / ソフトウェア開発における考慮"
    }
  ]
}
```

Field notes:

- `ts`: ISO8601 with timezone offset
- `git_repo_root`: `null` if the cwd is not inside a git repository
- `git_branch`: `null` if not applicable (e.g. not a git repo)
- `pr_number`: `null` unless a PR is obviously in context for this session
- `task_summary`: one short sentence

Serialize with `jq -c '.'` to produce a single line, then append:

```
printf '%s\n' "$json" >> ~/.claude/retrospective/notes/<project-slug>/YYYY-MM.jsonl
```

(`YYYY-MM` is the current year-month.)

## Step 5: Report

Report to the user in one short sentence:

```
retro-note recorded N findings to <path>
```

Do not use AskUserQuestion. Do not elaborate on individual findings in
chat — the detail lives in the jsonl record for later batch review.
