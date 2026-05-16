#!/usr/bin/env bash
# git-aicommit-edit: open the editor for a commit with an AI-drafted subject
# prefilled (via `git commit -e -m`). Wired in as the `git c` alias. Falls
# back to plain `git commit -e` on any AI failure, so claude being missing,
# slow, or broken never blocks the workflow — the user just edits a fresh
# buffer. To skip AI entirely, run `git commit` instead.

set -eu

# Nothing staged: hand off so git emits its own "nothing to commit" message.
if git diff --cached --quiet; then
  exec git commit "$@"
fi

# claude missing: open editor without AI subject.
if ! command -v claude >/dev/null 2>&1; then
  exec git commit -e "$@"
fi

# wc on macOS pads with spaces; tr handles both BSD and GNU output.
DIFF_BYTES=$(git diff --cached | wc -c | tr -d ' ')
# Defensive: skip AI if wc/git produce non-numeric output (would break the -gt test).
case "$DIFF_BYTES" in
  ''|*[!0-9]*) exec git commit -e "$@" ;;
esac
if [ "$DIFF_BYTES" -gt 200000 ]; then
  echo "git-aicommit-edit: staged diff is ${DIFF_BYTES} bytes, skipping AI" >&2
  exec git commit -e "$@"
fi

# || true: git log fails on the very first commit; empty RECENT is fine.
RECENT=$(git log -n 10 --pretty=format:'%s' 2>/dev/null || true)

PROMPT="Generate a single-line git commit subject for the staged diff piped on stdin.

Rules:
- One line only. No body. No trailing newline.
- Match the style and language of the recent commit subjects shown below
  (English-only repo -> English; Japanese-mixed repo -> use that style).
- 'verb: description' or 'Verb description' - follow the existing pattern.
- No surrounding quotes, no markdown, no preamble. Output ONLY the subject.

--- recent commit subjects (style + language reference) ---
$RECENT
--- end ---"

# Prefer GNU timeout if available; fall back to no timeout (macOS without coreutils).
TIMEOUT_BIN=""
if command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN="gtimeout"
elif command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="timeout"
fi

echo "git-aicommit-edit: drafting commit subject via claude haiku..." >&2

# Capture claude stderr so we can surface auth / rate-limit / etc. on failure.
ERR_FILE=$(mktemp -t git-aicommit-edit.err.XXXXXX)
trap 'rm -f "$ERR_FILE"' EXIT

# pipefail so a `git diff --cached` failure surfaces as RC, not masked by
# claude returning rc=0 on truncated input.
set +e
set -o pipefail
if [ -n "$TIMEOUT_BIN" ]; then
  GENERATED=$(git diff --cached | "$TIMEOUT_BIN" 25s claude --model haiku -p "$PROMPT" 2>"$ERR_FILE")
  RC=$?
else
  GENERATED=$(git diff --cached | claude --model haiku -p "$PROMPT" 2>"$ERR_FILE")
  RC=$?
fi
set +o pipefail
set -e

# First non-empty line only (defensive — model may emit preamble or fences).
SUBJECT=$(printf '%s\n' "$GENERATED" | awk 'NF{print; exit}' || true)

if [ "$RC" -ne 0 ] || [ -z "$SUBJECT" ]; then
  case "$RC" in
    124) echo "git-aicommit-edit: claude timed out after 25s, falling back to plain editor" >&2 ;;
    0)
      echo "git-aicommit-edit: claude returned empty output, falling back to plain editor" >&2
      ;;
    *)
      ERR_HEAD=$(head -n 1 "$ERR_FILE" 2>/dev/null || true)
      if [ -n "$ERR_HEAD" ]; then
        echo "git-aicommit-edit: claude failed rc=$RC ($ERR_HEAD), falling back to plain editor" >&2
      else
        echo "git-aicommit-edit: claude failed rc=$RC, falling back to plain editor" >&2
      fi
      ;;
  esac
  exec git commit -e "$@"
fi

exec git commit -e -m "$SUBJECT" "$@"
