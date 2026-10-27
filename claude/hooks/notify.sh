#!/bin/bash
# Notification hook: one macOS notification per event, naming the session
# and sounding per notification type, the same in any terminal.
#
# noti posts the notification and plays its sound in one call,
# independent of which terminal runs Claude Code. Claude Code's own
# notification is turned off with preferredNotifChannel so the two do not
# stack.
#
# The body says what the notification is about, read from the transcript:
# the pending tool call for permission_prompt, and a summary of Claude's
# last message for idle_prompt, drafted by `claude -p` on Haiku. Either
# falls back to Claude Code's own message when the transcript has nothing
# to read or the summary fails, so the notification still goes out.
set -eu

if ! command -v noti >/dev/null; then
  exit 0
fi

input=$(cat)
type=$(jq -r '.notification_type // empty' <<<"$input")
message=$(jq -r '.message // "Needs your attention"' <<<"$input")
session=$(jq -r '.session_title // empty' <<<"$input")
cwd=$(jq -r '.cwd // empty' <<<"$input")
transcript=$(jq -r '.transcript_path // empty' <<<"$input")

if [ -z "$session" ]; then
  session=${cwd##*/}
  branch=$(git -C "${cwd:-.}" branch --show-current 2>/dev/null || true)
  if [ -n "$branch" ]; then
    session="$session ($branch)"
  fi
fi

# Content blocks of the recent messages, oldest first. The transcript is
# written asynchronously and may lag the conversation, so each reader
# below returns nothing when the block it needs is not there yet.
recent_blocks() {
  if [ ! -f "$transcript" ]; then
    return 0
  fi
  tail -n 50 "$transcript" |
    jq -cs '[.[] | select(.type == "assistant" or .type == "user") | .message.content | arrays | .[]]'
}

# The pending call is the last tool call with no result logged, since
# results of parallel calls can land after it.
pending_tool() {
  recent_blocks | jq -r '
    (map(select(.type == "tool_result") | .tool_use_id)) as $done
    | map(select(.type == "tool_use" and (.id | IN($done[]) | not))) | last // empty
    | .name + ": " + ((.input.description // .input.command // .input.file_path // .input.url // "") | tostring)
    | .[0:120]'
}

summarize_last_message() {
  local text summary
  text=$(recent_blocks | jq -r 'last // empty | select(.type == "text") | .text')
  if [ -z "$text" ]; then
    return 0
  fi
  if [ "${#text}" -le 50 ]; then
    printf '%s\n' "$text"
    return 0
  fi
  # The flags and env vars match xdg-config/git/hooks/prepare-commit-msg,
  # which strips what a one-shot completion does not need. Skipping the
  # settings files also keeps the child from loading this hook again.
  # claude -p prints its errors to stdout, so a failed run returns
  # nothing rather than its output.
  summary=$(printf '%s' "$text" | tail -c 4000 |
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
      DISABLE_TELEMETRY=1 \
      DISABLE_ERROR_REPORTING=1 \
      DISABLE_AUTOUPDATER=1 \
      CLAUDE_CODE_DISABLE_THINKING=1 \
      timeout 20 claude -p \
      --model haiku \
      --effort low \
      --system-prompt "You condense the last message an AI coding assistant showed its user into a desktop notification. Write one Japanese sentence of at most 50 characters saying what the assistant is asking the user, or what it finished when it asks nothing. Output the sentence only, with no quotes, markdown, or preamble." \
      --safe-mode \
      --setting-sources "" \
      --tools "" \
      --strict-mcp-config \
      --disable-slash-commands \
      --no-session-persistence \
      --output-format text) || return 0
  head -n 1 <<<"$summary"
}

detail=''
case "$type" in
  permission_prompt)
    mark='🔐' sound=Submarine
    detail=$(pending_tool || true)
    ;;
  idle_prompt)
    mark='✅' sound=Glass
    if command -v claude >/dev/null; then
      detail=$(summarize_last_message || true)
    fi
    ;;
  elicitation_dialog | elicitation_url_dialog) mark='❓' sound=Ping ;;
  *) mark='🔔' sound=Pop ;;
esac

NOTI_NSUSER_SOUNDNAME=$sound noti --title "$mark ${session:-Claude Code}" --message "${detail:-$message}"
