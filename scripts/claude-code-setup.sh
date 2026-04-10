#!/usr/bin/env bash

# Claude Code CLI setup: registers MCP servers and installs plugins.
# Safe to run multiple times (idempotent).
# Counterpart to scripts/deploy.sh, which handles file symlinks only.

set -eu

if ! command -v claude >/dev/null 2>&1; then
  echo "Error: claude CLI is not installed" >&2
  exit 1
fi

# Wrapper: ignore "already exists" from claude mcp add-json, fail on real errors
mcp_add() {
  local output
  if output=$(claude mcp add-json --scope user "$@" 2>&1); then
    return 0
  fi
  if [[ "$output" == *"already exists"* ]]; then
    return 0
  fi
  echo "$output" >&2
  return 1
}

# --- MCP servers ---
# IDE-local servers (intellij-index, goland-index) are intentionally omitted
mcp_add deepwiki '{"type":"http","url":"https://mcp.deepwiki.com/mcp"}'
mcp_add Context7 '{"command":"npx","args":["-y","@upstash/context7-mcp"]}'

# --- Plugins ---
# marketplace add and plugin install are both idempotent
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex
claude plugin install pr-review-toolkit@claude-plugins-official
