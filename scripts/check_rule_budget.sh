#!/bin/bash

# Enforce a line-count budget on always-loaded AI rule files, so the
# rules that load into every session don't grow unbounded again.

set -eu

AIRULES_MAX=150
RULES_MAX=100

errors=0

check_budget() {
  local path="$1"
  local max="$2"
  local lines
  lines=$(wc -l < "$path" | tr -d ' ')
  if [ "$lines" -le "$max" ]; then
    echo "OK: $path ($lines / $max lines)"
  else
    echo "FAIL: $path is $lines lines, over the $max-line budget"
    errors=$((errors + 1))
  fi
}

check_budget AIRULES.md "$AIRULES_MAX"

for f in claude/rules/*.md; do
  check_budget "$f" "$RULES_MAX"
done

if [ "$errors" -gt 0 ]; then
  echo "FAILED: $errors rule file(s) over budget"
  exit 1
else
  echo "All rule files within budget"
fi
