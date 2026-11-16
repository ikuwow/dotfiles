#!/bin/bash

# Give a tmux pane slot several tabs, shown one at a time
# Usage: tabs.sh new|claude|next|prev|close|died|render <pane-id>
#
# Tmux key bindings and hooks run this with the pane they act on. A tab is
# a real pane: the shown one sits in the slot, and the others are parked,
# each in a window of its own in the session $store. Switching swaps a
# parked pane into the slot, so programs and scrollback keep running.
# The panes of one slot share the pane option @tab_group, and their order
# is the order of their pane IDs, which tmux hands out ascending.

set -eu

store=tabs-store
cmd="$1"
pane="$2"

info() {
  tmux display-message -p -t "$1" "$2"
}

# Group members as "pane-id session-name", in tab order
members() {
  tmux list-panes -a -F '#{@tab_group} #{pane_id} #{session_name}' |
    awk -v g="$1" '$1 == g { sub(/^%/, "", $2); print $2, $3 }' |
    sort -n | awk '{ print "%" $1, $2 }'
}

# A parked pane whose slot was killed some other way has no tab to return to
prune() {
  tmux list-panes -a -F '#{@tab_group} #{pane_id} #{session_name}' |
    awk -v s="$store" '$1 != "" { if ($3 == s) parked[$2] = $1; else shown[$1] = 1 }
      END { for (p in parked) if (!(parked[p] in shown)) print p }' |
    while read -r p; do tmux kill-pane -t "$p"; done
}

# A parked window takes the slot's size before a swap, so the program in
# the pane is not resized on each switch
swap_in() {
  tmux resize-window -t "$1" -x "$(info "$2" '#{pane_width}')" -y "$(info "$2" '#{pane_height}')"
  tmux swap-pane -d -Z -s "$1" -t "$2"
}

render() {
  local group shown list='' i=0 p label
  group="$(info "$1" '#{@tab_group}')"
  [ -n "$group" ] || return 0
  shown="$(members "$group" | awk -v s="$store" '$2 != s { print $1; exit }')"
  if [ "$(members "$group" | wc -l)" -lt 2 ]; then
    tmux set-option -pu -t "$shown" @tab_group ';' set-option -pu -t "$shown" @tab_list \
      ';' set-option -pu -t "$shown" remain-on-exit
    return 0
  fi
  # The shown tab's label stays a format, so it follows its pane live
  label="$(tmux show-options -gv @tab_label)"
  while read -r p _; do
    i=$((i + 1))
    if [ "$p" = "$shown" ]; then
      list="$list#[reverse] $i:#{E:@tab_label} #[noreverse]"
    else
      list="$list $i:$(info "$p" "$label" | sed 's/#/##/g') "
    fi
  done < <(members "$group")
  tmux set-option -p -t "$shown" @tab_list "$list"
}

prune
group="$(info "$pane" '#{@tab_group}')"

case "$cmd" in
  new | claude)
    if [ -z "$group" ]; then
      group="g${pane#%}"
      tmux set-option -p -t "$pane" @tab_group "$group" ';' set-option -p -t "$pane" remain-on-exit on
    fi
    if [ "$cmd" = claude ]; then dir="$(info "$pane" '#{session_path}')"; else dir="$(info "$pane" '#{pane_current_path}')"; fi
    # The store's first window is a placeholder that only lets it exist
    placeholder=''
    if ! tmux has-session -t "=$store" 2>/dev/null; then
      placeholder="$(tmux new-session -d -P -F '#{window_id}' -s "$store" -c /)"
    fi
    # A Claude Code tab runs claude as its program, so its tab closes with it
    if [ "$cmd" = claude ]; then set -- 'claude --ide'; else set --; fi
    tab="$(tmux new-window -d -P -F '#{pane_id}' -t "=$store:" -c "$dir" "$@")"
    if [ -n "$placeholder" ]; then tmux kill-window -t "$placeholder"; fi
    tmux set-option -p -t "$tab" @tab_group "$group" ';' set-option -p -t "$tab" remain-on-exit on
    swap_in "$tab" "$pane"
    tmux select-pane -t "$tab"
    ;;
  next | prev)
    if [ -z "$group" ]; then
      tmux display-message 'No other tab in this pane'
      exit 0
    fi
    step=1
    if [ "$cmd" = prev ]; then step=-1; fi
    target="$(members "$group" | awk -v p="$pane" -v d="$step" '{ ids[NR] = $1; if ($1 == p) at = NR }
      END { print ids[(at - 1 + d + NR) % NR + 1] }')"
    swap_in "$target" "$pane"
    tmux select-pane -t "$target"
    ;;
  close | died)
    # The pane-died hook fires for every pane left open on exit, tab or not
    if [ -z "$group" ]; then
      if [ "$cmd" = close ]; then tmux kill-pane -t "$pane"; fi
      exit 0
    fi
    shown="$(members "$group" | awk -v s="$store" '$2 != s { print $1; exit }')"
    # A shown tab that closes hands the slot to its neighbor
    if [ "$shown" = "$pane" ]; then
      next="$(members "$group" | awk -v p="$pane" '{ ids[NR] = $1; if ($1 == p) at = NR }
        END { if (NR > 1) print ids[at < NR ? at + 1 : at - 1] }')"
      if [ -n "$next" ]; then
        active="$(info "$pane" '#{pane_active}')"
        swap_in "$next" "$pane"
        if [ "$active" = 1 ]; then tmux select-pane -t "$next"; fi
        shown="$next"
      fi
    fi
    tmux kill-pane -t "$pane"
    if [ "$shown" = "$pane" ]; then exit 0; fi
    pane="$shown"
    ;;
  render) ;;
  *)
    echo "Error: unknown command: $cmd" >&2
    exit 1
    ;;
esac

render "$pane"
