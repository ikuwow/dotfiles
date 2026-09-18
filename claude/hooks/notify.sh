#!/bin/bash
# Notification hook: raise a macOS notification that names the session.
#
# With several sessions open at once, the title carries the project
# directory and git branch so the notification says which session wants
# attention, and the body carries Claude Code's own message, which says
# what it wants (a permission, an answer, a reply). Which notification
# types reach this script is decided by the matcher in
# claude/settings.json.
set -eu

if ! command -v noti >/dev/null; then
  exit 0
fi

input=$(cat)
cwd=$(jq -r '.cwd // empty' <<<"$input")
message=$(jq -r '.message // "Requires response."' <<<"$input")

title=${cwd##*/}
title=${title:-Claude Code}
branch=$(git -C "${cwd:-.}" branch --show-current 2>/dev/null || true)
if [ -n "$branch" ]; then
  title="$title ($branch)"
fi

NOTI_NSUSER_SOUNDNAME=Submarine noti --title "$title" --message "$message"
