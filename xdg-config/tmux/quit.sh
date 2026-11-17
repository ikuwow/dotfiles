#!/bin/bash

# Quit the programs of a tmux session the way their user would, stopping
# at the first one that stays
# Usage: quit.sh <session-id> <client>
#
# Bound to a key in tmux.conf. The session's panes and the tabs tabs.sh
# keeps for its slots go in three rounds: nvim gets :qa, which refuses
# while a buffer has unsaved changes; Claude Code gets Ctrl-D twice; a
# shell gets Ctrl-D once, which bash refuses while it has stopped jobs.
# A program still running at the end of its round ends the run with a
# message naming its pane. The session closes with its last pane.

set -eu

session="$1"
client="$2"
store=tabs-store
shells='^(bash|zsh|sh|fish)$'

report() {
  tmux display-message -c "$client" "quit: $1"
}

# The tab groups shown in the session, fixed at the start: a tab that
# leaves the store takes its group into the session
groups=" $(tmux list-panes -s -t "$session" -F '#{@tab_group}' | tr '\n' ' ') "

# The panes in scope as "pane-id command claude-state": with "store" the
# parked tabs of the session's slots, with "session" the session's own
panes() {
  if [ "$1" = store ]; then
    if tmux has-session -t "=$store" 2>/dev/null; then
      tmux list-panes -s -t "=$store" -F '#{@tab_group} #{pane_id} #{pane_current_command} #{@claude_state}' |
        while read -r group rest; do
          case "$groups" in *" $group "*) if [ -n "$group" ]; then echo "$rest"; fi ;; esac
        done
    fi
  elif tmux has-session -t "$session" 2>/dev/null; then
    tmux list-panes -s -t "$session" -F '#{pane_id} #{pane_current_command} #{@claude_state}'
  fi
}

# The first pane in scope $1 whose command matches the regex $2
first() {
  panes "$1" | awk -v re="$2" '$2 ~ re { print $1; exit }'
}

# Send the keys after $3 to every pane in scope $1 running a command that
# matches the regex $2, and wait up to 5 seconds for them all to exit.
# Parked tabs go before the session's panes, since a shown tab that exits
# while a tab of its slot is still closing can be left dead in the slot.
quit() {
  local scope="$1" re="$2" pane _
  shift 2
  panes "$scope" | awk -v re="$re" '$2 ~ re { print $1 }' | while read -r pane; do
    # A pane that dies between the listing and the keys needs none
    tmux send-keys -t "$pane" "$@" 2>/dev/null || true
  done
  for _ in $(seq 25); do
    if [ -z "$(first "$scope" "$re")" ]; then
      # Leave tabs.sh time to drop the closed tabs from their slots
      sleep 0.5
      return 0
    fi
    sleep 0.2
  done
  report "$(panes "$scope" | awk -v re="$re" '$2 ~ re { print $2 " in pane " $1; exit }') did not exit"
  exit 0
}

# Nothing is sent while any pane runs something this script cannot quit,
# or a Claude Code session that its hooks have not marked idle
while read -r pane cmd state; do
  if [[ "$cmd" =~ $shells ]] || [ "$cmd" = nvim ]; then
    continue
  fi
  if [ "$cmd" != claude ]; then
    report "pane $pane runs $cmd"
    exit 0
  fi
  if [ "$state" != idle ]; then
    report "claude in pane $pane is ${state:-in an unknown state}"
    exit 0
  fi
done < <(panes store; panes session)

for re in '^nvim$' '^claude$' "$shells"; do
  case "$re" in
    '^nvim$') set -- Escape ':qa' Enter ;;
    '^claude$') set -- C-d C-d ;;
    *) set -- C-d ;;
  esac
  quit store "$re" "$@"
  quit session "$re" "$@"
done
