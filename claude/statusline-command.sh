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

# Line 1: model, context, lines changed
CTX_COLOR=$(color_for_pct "$CONTEXT_PCT")
printf '%b' "🤖 ${MODEL}${SEP}📊 ${CTX_COLOR}${CONTEXT_PCT}%${RESET}${SEP}✏️ +${LINES_ADDED}/-${LINES_REMOVED}${SEP}\n"
