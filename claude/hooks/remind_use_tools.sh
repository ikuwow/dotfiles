#!/bin/bash
# Remind to use Glob/Grep/Read tools instead of the find command

set -eu

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -qE '^find '; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: "find command detected. Can you use Glob/Grep/Read tools instead? Allow if find is truly needed."
    }
  }'
fi
