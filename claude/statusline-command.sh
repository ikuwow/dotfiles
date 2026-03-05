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

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "N/A")

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

progress_bar() {
  local pct=$1
  local filled=$(( pct / 10 ))
  local empty=$(( 10 - filled ))
  local color
  color=$(color_for_pct "$pct")
  local bar=""
  for ((i=0; i<filled; i++)); do
    bar+="▰"
  done
  for ((i=0; i<empty; i++)); do
    bar+="▱"
  done
  printf '%b' "${color}${bar} ${pct}%${RESET}"
}

# Line 1: model, context, lines changed, branch
CTX_COLOR=$(color_for_pct "$CONTEXT_PCT")
printf '%b' "🤖 ${MODEL}${SEP}📊 ${CTX_COLOR}${CONTEXT_PCT}%${RESET}${SEP}✏️ +${LINES_ADDED}/-${LINES_REMOVED}${SEP}🔀 ${BRANCH}\n"

# Rate limit usage via Anthropic API
CACHE_FILE="/tmp/claude-usage-cache.json"
CACHE_TTL=360

fetch_usage() {
  local token
  token=$(security find-generic-password -s "claude-api-credential" -w 2>/dev/null || echo "")
  if [ -z "$token" ]; then
    return 1
  fi

  local response
  response=$(curl -sf -H "Authorization: Bearer ${token}" \
    "https://api.anthropic.com/api/oauth/usage" 2>/dev/null || echo "")
  if [ -z "$response" ]; then
    return 1
  fi

  echo "$response" > "$CACHE_FILE"
}

get_usage() {
  local now
  now=$(date +%s)

  if [ -f "$CACHE_FILE" ]; then
    local mtime
    mtime=$(stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0)
    local age=$(( now - mtime ))
    if [ "$age" -gt "$CACHE_TTL" ]; then
      fetch_usage || true
    fi
  else
    fetch_usage || true
  fi

  if [ ! -f "$CACHE_FILE" ]; then
    return 1
  fi
  cat "$CACHE_FILE"
}

format_reset_time() {
  local iso_time=$1
  if [ -z "$iso_time" ] || [ "$iso_time" = "null" ]; then
    echo "N/A"
    return
  fi
  TZ=Asia/Tokyo date -jf "%Y-%m-%dT%H:%M:%S" "${iso_time%%.*}" "+%m/%d %H:%M" 2>/dev/null || echo "$iso_time"
}

USAGE=$(get_usage || echo "")

if [ -n "$USAGE" ]; then
  FIVE_HOUR_PCT=$(echo "$USAGE" | jq -r '(.five_hour.utilization // 0) * 100 | floor')
  FIVE_HOUR_RESET=$(echo "$USAGE" | jq -r '.five_hour.reset_at // ""')
  SEVEN_DAY_PCT=$(echo "$USAGE" | jq -r '(.seven_day.utilization // 0) * 100 | floor')
  SEVEN_DAY_RESET=$(echo "$USAGE" | jq -r '.seven_day.reset_at // ""')

  FIVE_RESET_FMT=$(format_reset_time "$FIVE_HOUR_RESET")
  SEVEN_RESET_FMT=$(format_reset_time "$SEVEN_DAY_RESET")

  printf '%b' "⏳ 5h  $(progress_bar "$FIVE_HOUR_PCT") ${GREY}reset ${FIVE_RESET_FMT}${RESET}\n"
  printf '%b' "📅 7d  $(progress_bar "$SEVEN_DAY_PCT") ${GREY}reset ${SEVEN_RESET_FMT}${RESET}\n"
else
  printf '%b' "⏳ 5h  ${GREY}(usage unavailable)${RESET}\n"
  printf '%b' "📅 7d  ${GREY}(usage unavailable)${RESET}\n"
fi
