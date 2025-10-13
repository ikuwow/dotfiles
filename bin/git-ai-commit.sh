#!/usr/bin/env bash
set -euo pipefail

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

COMMIT_MSG=$(echo "$PROMPT" | codex exec -)

echo "Generated commit message:" >&2
echo "$COMMIT_MSG" >&2
echo "" >&2

TEMP_MSG=$(mktemp)
echo "$COMMIT_MSG" > "$TEMP_MSG"

git commit -t "$TEMP_MSG"

rm -f "$TEMP_MSG"
