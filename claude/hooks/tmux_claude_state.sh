#!/bin/bash
# Mark the tmux pane running this Claude Code session as idle or busy, in
# the pane option @claude_state, which xdg-config/tmux/quit.sh reads so it
# quits only an idle session.
# Usage: tmux_claude_state.sh idle|busy
#
# A session outside tmux has no pane to mark. The mark is best effort: a
# failure here must not show up as a hook error on every prompt and tool
# call.

if [ -n "${TMUX_PANE:-}" ]; then
  tmux set-option -p -t "$TMUX_PANE" @claude_state "$1" 2>/dev/null || true
fi
