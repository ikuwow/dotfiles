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
# OBSIDIAN_API_KEY is expanded from process env by Claude Code at MCP server
# launch time; set it in ~/.bash_profile.local. Host/port are hardcoded since
# they're not secret and Claude Code's diagnostics warn about missing env vars.
# shellcheck disable=SC2016
mcp_add mcp-obsidian '{"command":"uvx","args":["mcp-obsidian"],"env":{"OBSIDIAN_API_KEY":"${OBSIDIAN_API_KEY}","OBSIDIAN_HOST":"127.0.0.1","OBSIDIAN_PORT":"27123"}}'

# --- Plugins ---
# Ensure marketplaces exist (required on fresh environments like Claude Code web).
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex
claude plugin install pr-review-toolkit@claude-plugins-official
claude plugin install gopls-lsp@claude-plugins-official
claude plugin install session-report@claude-plugins-official
claude plugin install claude-md-management@claude-plugins-official
claude plugin install skill-creator@claude-plugins-official
claude plugin install claude-code-setup@claude-plugins-official
claude plugin install hookify@claude-plugins-official
claude plugin install security-guidance@claude-plugins-official
