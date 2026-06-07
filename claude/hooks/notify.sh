#!/bin/bash

# Consolidated Notification / Stop / SubagentStop hook for Claude Code.
#
# Reads the hook stdin JSON for the event name and cwd, picks a
# per-event system sound, and renders a macOS notification with
# repo + branch in the title so parallel sessions stay distinguishable.
#
# Replaces the previous `noti` setup. Native macOS only — no Homebrew
# dependency.
#
# Event matrix:
#   Stop                                 → Glass     (clean finish)
#   SubagentStop                         → Pop       (subagent done, lighter)
#   Notification (permission_prompt)     → Submarine (waiting on user)
#   Notification (idle_prompt)           → Ping      (long idle)
#   Notification (anything else)         → Blow      (generic input needed)
#
# Issue: ikuwow/dotfiles#148.

set -u

payload="$(cat)"

event="$(echo "$payload" | jq -r '.hook_event_name // ""')"
cwd="$(echo "$payload" | jq -r '.cwd // ""')"
matcher="$(echo "$payload" | jq -r '.message // ""')"

repo="$(basename "${cwd:-$PWD}")"
branch=""
if [ -n "$cwd" ] && [ -d "$cwd/.git" ] || git -C "${cwd:-$PWD}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    branch="$(git -C "${cwd:-$PWD}" branch --show-current 2>/dev/null || true)"
fi

title="Claude Code · $repo"
if [ -n "$branch" ]; then
    title="$title ($branch)"
fi

case "$event" in
    Stop)
        sound="Glass"
        message="Done."
        ;;
    SubagentStop)
        sound="Pop"
        message="Subagent done."
        ;;
    Notification)
        case "$matcher" in
            *permission*) sound="Submarine"; message="Permission requested." ;;
            *idle*)       sound="Ping";      message="Idle." ;;
            *)            sound="Blow";      message="Input requested." ;;
        esac
        ;;
    *)
        sound="Tink"
        message="$event"
        ;;
esac

sound_path="/System/Library/Sounds/${sound}.aiff"
if [ -f "$sound_path" ]; then
    afplay "$sound_path" >/dev/null 2>&1 &
fi

osascript -e "display notification \"$message\" with title \"$title\"" >/dev/null 2>&1 || true

exit 0
