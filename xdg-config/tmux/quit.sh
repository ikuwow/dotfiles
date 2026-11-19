#!/bin/bash

# Quit the programs of a tmux session the way their user would
# Usage: quit.sh <session-id> <client>
#
# Bound to a key in tmux.conf. Each pass sends every pane of the session
# the keys for its program: nvim gets :qa, which refuses while a buffer
# has unsaved changes; Claude Code gets Ctrl-D twice; a shell gets Ctrl-D
# once, which bash refuses while it has stopped jobs. A program that
# exits leaves its pane to its shell, or closes the pane, and tabs.sh then
# shows the next tab of its slot, so passes repeat until the session
# closes with its last pane, or until a pass changes nothing, which ends
# the run with a message naming the panes left.

set -eu

session="$1"
client="$2"

# display-message passes its message through strftime, which would read
# the % of a pane ID
report() {
  tmux display-message -c "$client" "quit: ${1//%/%%}"
}

# The session's live panes as "pane-id:command", empty once it has
# closed; a tab whose program has exited stays dead until tabs.sh closes it
panes() {
  tmux list-panes -s -t "$session" -F '#{?pane_dead,,#{pane_id}:#{pane_current_command}}' 2>/dev/null |
    grep . || true
}

# Each pane gets the keys for a program once, since a second Ctrl-D makes
# bash exit with its stopped jobs
sent=' '
while [ -n "$(panes)" ]; do
  before="$(panes)"
  # Nothing more is sent once a pane runs something this script cannot quit
  other="$(echo "$before" | grep -vE ':(nvim|claude|bash|zsh|sh|fish)$' | head -n 1)"
  if [ -n "$other" ]; then
    report "pane ${other%%:*} runs ${other#*:}"
    exit 0
  fi
  for pane in $before; do
    case "$sent" in *" $pane "*) continue ;; esac
    case "${pane#*:}" in
      nvim) set -- Escape :qa Enter ;;
      claude) set -- C-d C-d ;;
      *) set -- C-d ;;
    esac
    # A pane that closes between the listing and the keys needs none
    tmux send-keys -t "${pane%%:*}" "$@" 2>/dev/null || true
    sent="$sent$pane "
  done
  for _ in $(seq 25); do
    if [ "$(panes)" != "$before" ]; then
      continue 2
    fi
    sleep 0.2
  done
  report "left $(echo "$before" | tr '\n' ' ')"
  exit 0
done
