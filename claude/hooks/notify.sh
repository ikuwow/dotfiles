#!/bin/bash
# Notification hook: one macOS notification per event, naming the session
# and sounding per notification type, the same in any terminal.
#
# noti posts the notification and plays its sound in one call,
# independent of which terminal runs Claude Code. Claude Code's own
# notification is turned off with preferredNotifChannel so the two do not
# stack.
set -eu

if ! command -v noti >/dev/null; then
  exit 0
fi

input=$(cat)
type=$(jq -r '.notification_type // empty' <<<"$input")
message=$(jq -r '.message // "Needs your attention"' <<<"$input")
session=$(jq -r '.session_title // empty' <<<"$input")
cwd=$(jq -r '.cwd // empty' <<<"$input")

if [ -z "$session" ]; then
  session=${cwd##*/}
  branch=$(git -C "${cwd:-.}" branch --show-current 2>/dev/null || true)
  if [ -n "$branch" ]; then
    session="$session ($branch)"
  fi
fi

case "$type" in
  permission_prompt) mark='🔐' sound=Submarine ;;
  idle_prompt) mark='✅' sound=Glass ;;
  elicitation_dialog | elicitation_url_dialog) mark='❓' sound=Ping ;;
  *) mark='🔔' sound=Pop ;;
esac

NOTI_NSUSER_SOUNDNAME=$sound noti --title "$mark ${session:-Claude Code}" --message "$message"
