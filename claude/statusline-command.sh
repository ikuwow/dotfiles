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
CONTEXT_PCT=$(echo "$INPUT" | jq -r '.context_window.used_percentage // 0')
LINES_ADDED=$(echo "$INPUT" | jq -r '.cost.total_lines_added // 0')
LINES_REMOVED=$(echo "$INPUT" | jq -r '.cost.total_lines_removed // 0')
# used_percentage is a float; round it for the integer comparisons below.
FIVE_HOUR_PCT=$(echo "$INPUT" | jq -r '.rate_limits.five_hour.used_percentage // empty | round')
FIVE_HOUR_RESETS_AT=$(echo "$INPUT" | jq -r '.rate_limits.five_hour.resets_at // empty')

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

# Higher effort costs more latency/budget, so color by intensity
# (default green covers low/medium and any future/unknown level).
color_for_effort() {
  case "$1" in
    xhigh|max) printf '%s' "$RED" ;;
    high) printf '%s' "$YELLOW" ;;
    *) printf '%s' "$GREEN" ;;
  esac
}

# The effort object is absent on models without the parameter, so
# .effort.level // "" yields ""; drop the segment instead of a placeholder.
EFFORT_SEG=""
if [ -n "$EFFORT" ]; then
  EFFORT_COLOR=$(color_for_effort "$EFFORT")
  EFFORT_SEG="⚡ ${EFFORT_COLOR}${EFFORT}${RESET}${SEP}"
fi

# rate_limits is present only for claude.ai subscribers and only after the
# session's first API response; drop the segment until it arrives.
RATE_SEG=""
if [ -n "$FIVE_HOUR_PCT" ]; then
  RATE_COLOR=$(color_for_pct "$FIVE_HOUR_PCT")
  RATE_SEG="⏳ ${RATE_COLOR}${FIVE_HOUR_PCT}%${RESET}"
  if [ -n "$FIVE_HOUR_RESETS_AT" ]; then
    # BSD date takes -r <epoch>; GNU date takes -d @<epoch>.
    RESETS_HM=$(date -r "$FIVE_HOUR_RESETS_AT" +%H:%M 2>/dev/null || date -d "@$FIVE_HOUR_RESETS_AT" +%H:%M)
    RATE_SEG="${RATE_SEG} (→${RESETS_HM})"
  fi
  RATE_SEG="${RATE_SEG}${SEP}"
fi

# Line 1: model, effort, context, 5-hour rate limit, lines changed
CTX_COLOR=$(color_for_pct "$CONTEXT_PCT")
printf '%b' "🤖 ${MODEL}${SEP}${EFFORT_SEG}📊 ${CTX_COLOR}${CONTEXT_PCT}%${RESET}${SEP}${RATE_SEG}✏️ +${LINES_ADDED}/-${LINES_REMOVED}${SEP}\n"
