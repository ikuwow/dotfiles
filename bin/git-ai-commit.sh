#!/usr/bin/env bash
set -euo pipefail

DEBUG=false
if [[ "${1:-}" == "--debug" ]]; then
    DEBUG=true
    shift
fi

DIFF=$(git diff --staged)

if [ -z "$DIFF" ]; then
    echo "No staged changes found." >&2
    exit 1
fi

echo "Generating commit message..." >&2
PROMPT="Generate an appropriate commit message based on the git diff output below.
Do NOT execute the git diff command.
Format: \"verb: description\" in a single concise line.
Output ONLY the commit message in English, without any additional explanation or text.

--- git diff output ---
$DIFF
--- end of diff ---"

if [ "$DEBUG" = true ]; then
    COMMIT_MSG=$(echo "$PROMPT" | codex exec -)
else
    COMMIT_MSG=$(echo "$PROMPT" | codex exec - 2>/dev/null)
fi

if [ -z "$COMMIT_MSG" ]; then
    echo "Failed to generate commit message." >&2
    exit 1
fi

echo "" >&2
echo "Commit message:" >&2
echo "  $COMMIT_MSG" >&2
echo "" >&2

read -p "Commit? (y/N): " -n 1 -r >&2
echo >&2
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled." >&2
    exit 1
fi

git commit -m "$COMMIT_MSG"
