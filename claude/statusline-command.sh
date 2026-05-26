#!/usr/bin/env bash

set -eu

# Colors (24-bit true color)
GREEN='\033[38;2;151;201;195m'
YELLOW='\033[38;2;229;192;123m'
RED='\033[38;2;224;108;117m'
GREY='\033[38;2;74;88;92m'
RESET='\033[0m'

SEP="${GREY} | ${RESET}"

# Read session JSON from stdin
INPUT=$(cat)

MODEL=$(echo "$INPUT" | jq -r '.model.display_name // "Unknown"')
EFFORT=$(echo "$INPUT" | jq -r '.effort.level // ""')
THINKING=$(echo "$INPUT" | jq -r '.thinking.enabled // false')
CONTEXT_PCT=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0')
LINES_ADDED=$(echo "$INPUT" | jq -r '.cost.total_lines_added // 0')
LINES_REMOVED=$(echo "$INPUT" | jq -r '.cost.total_lines_removed // 0')

color_for_pct() {
  local pct=$1
  if [ "$pct" -ge 80 ]; then
    printf '%s' "$RED"
  elif [ "$pct" -ge 50 ]; then
    printf '%s' "$YELLOW"
  else
    printf '%s' "$GREEN"
  fi
}

# Higher effort costs more latency/budget, so color by intensity.
color_for_effort() {
  case "$1" in
    xhigh|max) printf '%s' "$RED" ;;
    high) printf '%s' "$YELLOW" ;;
    *) printf '%s' "$GREEN" ;;
  esac
}

# effort.level is absent when the model does not support the parameter;
# drop the whole segment in that case rather than printing a placeholder.
EFFORT_SEG=""
if [ -n "$EFFORT" ]; then
  EFFORT_COLOR=$(color_for_effort "$EFFORT")
  EFFORT_SEG="⚡${EFFORT_COLOR}${EFFORT}${RESET}${SEP}"
fi

if [ "$THINKING" = "true" ]; then
  THINKING_SEG="🧠${GREEN}on${RESET}${SEP}"
else
  THINKING_SEG="🧠${GREY}off${RESET}${SEP}"
fi

# Line 1: model, effort, thinking, context, lines changed
CTX_COLOR=$(color_for_pct "$CONTEXT_PCT")
printf '%b' "🤖 ${MODEL}${SEP}${EFFORT_SEG}${THINKING_SEG}📊 ${CTX_COLOR}${CONTEXT_PCT}%${RESET}${SEP}✏️ +${LINES_ADDED}/-${LINES_REMOVED}${SEP}\n"
