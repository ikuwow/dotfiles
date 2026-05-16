#!/usr/bin/env bash
# git-aicommit-edit: open the editor for a commit with an AI-drafted subject
# prefilled (via `git commit -e -m`). Wired in as the `git c` alias. Falls
# back to plain `git commit -e` on any AI failure, so claude being missing,
# slow, or broken never blocks the workflow — the user just edits a fresh
# buffer.

set -eu

# Nothing staged: hand off so git emits its own "nothing to commit" message.
if git diff --cached --quiet; then
  exec git commit "$@"
fi

# Detect git flags that supply or amend the message themselves — in those
# cases injecting -m "$SUBJECT" would silently overwrite the user's
# existing/explicit message (e.g. `git c --amend --no-edit` would replace
# the previous commit's subject with a fresh AI draft, without prompting).
# When any such flag is present, skip AI and let git handle the message
# exactly as it would without this alias.
HAS_MSG_FLAG=0
for arg in "$@"; do
  case "$arg" in
    --amend|--no-edit|-c|-c=*|--reedit-message|--reedit-message=*|-C|-C=*|--reuse-message|--reuse-message=*|--squash|--squash=*|--fixup|--fixup=*|-F|-F=*|--file|--file=*|-t|-t=*|--template|--template=*|-m|-m=*|--message|--message=*)
      HAS_MSG_FLAG=1
      break
      ;;
  esac
done
if [ "$HAS_MSG_FLAG" = "1" ]; then
  exec git commit "$@"
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "git-aicommit-edit: claude not on PATH, falling back to plain editor" >&2
  exec git commit -e "$@"
fi

# wc on macOS pads with spaces; tr handles both BSD and GNU output.
DIFF_BYTES=$(git diff --cached | wc -c | tr -d ' ')
# Empty/non-numeric would error the -gt test under set -eu and skip the fallback.
case "$DIFF_BYTES" in
  ''|*[!0-9]*)
    echo "git-aicommit-edit: could not determine staged diff size (got '$DIFF_BYTES'), falling back to plain editor" >&2
    exec git commit -e "$@"
    ;;
esac
MAX_DIFF_BYTES=200000
if [ "$DIFF_BYTES" -gt "$MAX_DIFF_BYTES" ]; then
  echo "git-aicommit-edit: staged diff is ${DIFF_BYTES} bytes (threshold ${MAX_DIFF_BYTES}), falling back to plain editor" >&2
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

# Fall back to no timeout on macOS without coreutils (no gtimeout/timeout).
TIMEOUT_BIN=""
if command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN="gtimeout"
elif command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="timeout"
else
  echo "git-aicommit-edit: no timeout binary available, claude will run unbounded" >&2
fi

echo "git-aicommit-edit: drafting commit subject via claude haiku..." >&2

# Capture claude stderr so we can surface auth / rate-limit / etc. on failure.
ERR_FILE=$(mktemp -t git-aicommit-edit.err.XXXXXX)
# trap as belt-and-suspenders for non-exec exits; exec paths rm explicitly
# because trap on EXIT does NOT fire when the shell is replaced by exec.
trap 'rm -f "$ERR_FILE"' EXIT

# pipefail so a `git diff --cached` failure surfaces as RC, not masked by
# claude returning rc=0 on truncated input. Must stay paired with the
# `set +o pipefail` after the pipeline so it doesn't leak.
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
SUBJECT=$(printf '%s\n' "$GENERATED" | awk 'NF{print; exit}')
# Strip wrapping quotes and a single leading/trailing backtick — common
# claude output shapes that would otherwise land literally in the buffer.
SUBJECT=${SUBJECT#\"}; SUBJECT=${SUBJECT%\"}
SUBJECT=${SUBJECT#\'}; SUBJECT=${SUBJECT%\'}
SUBJECT=${SUBJECT#\`}; SUBJECT=${SUBJECT%\`}

if [ "$RC" -ne 0 ] || [ -z "$SUBJECT" ]; then
  case "$RC" in
    124) echo "git-aicommit-edit: claude timed out after 25s, falling back to plain editor" >&2 ;;
    0) echo "git-aicommit-edit: claude returned empty output, falling back to plain editor" >&2 ;;
    *)
      ERR_HEAD=$(head -c 200 "$ERR_FILE" 2>/dev/null | head -n 1 || true)
      if [ -n "$ERR_HEAD" ]; then
        echo "git-aicommit-edit: claude failed rc=$RC ($ERR_HEAD), falling back to plain editor" >&2
      else
        echo "git-aicommit-edit: claude failed rc=$RC, falling back to plain editor" >&2
      fi
      ;;
  esac
  rm -f "$ERR_FILE"
  exec git commit -e "$@"
fi

rm -f "$ERR_FILE"
exec git commit -e -m "$SUBJECT" "$@"
