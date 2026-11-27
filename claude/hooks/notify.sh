#!/bin/bash
# Notification hook: at most one macOS notification per event, naming the
# session.
#
# Ghostty posts it when its tab shows the session out of focus, so a click
# focuses that tab; the OSC 777 sequence goes to the client's tty,
# bypassing tmux. Ghostty shows nothing for the focused surface, so then a
# pane on screen gets only the sound, and a hidden pane gets noti, as other
# terminals do. Claude Code's own notification is off
# (preferredNotifChannel) so the two do not stack.
#
# The body says what the notification is about, read from the transcript:
# the pending tool call for permission_prompt, and a summary of Claude's
# last message for idle_prompt, drafted by `claude -p` on Haiku. Either
# falls back to Claude Code's own message when no body comes out, so the
# notification still goes out.
set -eu

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

# Content blocks of the recent messages, oldest first, each tagged with
# the role that wrote it. The docs say the transcript may lag the
# conversation, so a block the readers below need may not be there yet.
recent_blocks() {
  tail -n 50 "$transcript" |
    jq -cs '[.[] | select(.type == "assistant" or .type == "user") | .type as $role | .message.content | arrays | .[] | .role = $role]'
}

# Take the first tool call with no result logged: of parallel calls, the
# ones needing approval are prompted in order, and later calls also lack
# a result while the first waits.
pending_tool() {
  recent_blocks | jq -r '
    (map(select(.type == "tool_result") | .tool_use_id)) as $done
    | map(select(.type == "tool_use" and (.id | IN($done[]) | not))) | first // empty
    | .name + ": " + ((.input.description // .input.command // .input.file_path // .input.url // "") | tostring)
    | .[0:120]'
}

summarize_last_message() {
  local text summary
  text=$(recent_blocks | jq -r 'last // empty | select(.role == "assistant" and .type == "text") | .text')
  if [ -z "$text" ]; then
    return 0
  fi
  if [ "${#text}" -le 30 ]; then
    printf '%s\n' "$text"
    return 0
  fi
  # The flags and env vars strip what a one-shot completion does not need;
  # xdg-config/git/hooks/prepare-commit-msg explains each. --safe-mode
  # also disables hooks, so the child does not run this hook again.
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
      --system-prompt "You turn the last message an AI coding assistant showed its user into the body of a desktop notification, which shows about 30 characters. Write a terse Japanese phrase of at most 30 characters, ending in a noun or a bare verb stem, saying what the user is asked to do or decide, or what was finished when nothing is asked. Do not describe the message itself, and drop subjects, politeness, and detail. Name a topic only when the message itself names it; the examples carry no topic to copy. Output the phrase only, with no quotes, markdown, or preamble. Examples: 3案から選択待ち / PR 作成、CI 待ち / 片付け完了" \
      --safe-mode \
      --setting-sources "" \
      --tools "" \
      --strict-mcp-config \
      --disable-slash-commands \
      --no-session-persistence \
      --output-format text) || return 0
  head -n 1 <<<"$summary"
}

# A tab parked by xdg-config/tmux/tabs.sh sits in tabs-store, so its
# session is the one showing a tab of the same group.
ghostty_client() {
  local s group
  if [ -z "${TMUX_PANE:-}" ]; then
    return 0
  fi
  s=$(tmux display-message -p -t "$TMUX_PANE" '#{session_name}')
  if [ "$s" = tabs-store ]; then
    group=$(tmux display-message -p -t "$TMUX_PANE" '#{@tab_group}')
    if [ -z "$group" ]; then
      return 0
    fi
    s=$(tmux list-panes -a -F '#{@tab_group} #{session_name}' |
      awk -v g="$group" '$1 == g && $2 != "tabs-store" { print $2; exit }')
  fi
  if [ -z "$s" ]; then
    return 0
  fi
  tmux list-clients -t "=$s" -F '#{client_termname} #{client_tty} #{client_flags}' |
    awk '$1 == "xterm-ghostty" { print $2, $3; exit }'
}

pane_hidden() {
  tmux display-message -p -t "$TMUX_PANE" \
    '#{?#{==:#{session_name},tabs-store},1,#{?window_active,#{?window_zoomed_flag,#{?pane_active,0,1},0},1}}'
}

# OSC ends at BEL or ESC, and Ghostty ends the title at the first ";".
osc_field() {
  LC_ALL=C tr -d '\000-\037\177' | tr ';' ','
}

if ! command -v noti >/dev/null && [ -z "$(ghostty_client || true)" ]; then
  exit 0
fi

detail=''
case "$type" in
  permission_prompt)
    mark='🔐' kind='許可待ち' sound=Submarine
    detail=$(pending_tool || true)
    ;;
  idle_prompt)
    mark='✅' kind='入力待ち' sound=Glass
    detail=$(summarize_last_message || true)
    ;;
  elicitation_dialog | elicitation_url_dialog) mark='❓' kind='質問' sound=Ping ;;
  *) mark='🔔' kind='通知' sound=Pop ;;
esac

title="$mark ${session:-Claude Code}"
body=${detail:-$message}

# After the body, which claude -p can take 20 seconds to draft.
read -r tty flags <<<"$(ghostty_client || true)" || true
case ",${flags:-}," in
  *,focused,*) focused=1 ;;
  *) focused=0 ;;
esac

if [ -n "$tty" ] && [ -w "$tty" ] && [ "$focused" = 0 ]; then
  # Ghostty adds the tab title as the subtitle, which names this session
  # only while this pane is the one on screen
  if [ "$(pane_hidden || true)" = 0 ]; then
    title="$mark $kind"
  fi
  printf '\033]777;notify;%s;%s\007' "$(osc_field <<<"$title")" "$(osc_field <<<"$body")" >"$tty"
elif [ "$focused" = 1 ] && [ "$(pane_hidden || true)" = 0 ]; then
  afplay "/System/Library/Sounds/$sound.aiff"
elif command -v noti >/dev/null; then
  NOTI_NSUSER_SOUNDNAME=$sound noti --title "$title" --message "$body"
fi
