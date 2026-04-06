#!/usr/bin/env bash

# Claude Code CLI setup: registers MCP servers and installs plugins.
# Safe to run multiple times (idempotent).
# Counterpart to scripts/deploy.sh, which handles file symlinks only.

set -euo pipefail

SETTINGS_FILE="$HOME/.claude/settings.json"
MCP_CONFIG_FILE="$HOME/.claude/.mcp.json"

# Known marketplace name -> GitHub repo mappings (for non-builtin marketplaces)
declare -A MARKETPLACE_REPOS=(
  ["openai-codex"]="openai/codex-plugin-cc"
)

# Marketplace always registered by Claude Code itself; skip manual registration
BUILTIN_MARKETPLACE="claude-plugins-official"

# --- Prerequisite checks ---

if ! command -v jq > /dev/null 2>&1; then
  echo "Error: jq is required but not installed" >&2
  exit 1
fi

if ! command -v claude > /dev/null 2>&1; then
  echo "Error: claude CLI is required but not installed" >&2
  exit 1
fi

# --- MCP servers ---

if [[ ! -f "$MCP_CONFIG_FILE" ]]; then
  echo "Warning: MCP config not found at $MCP_CONFIG_FILE, skipping MCP setup" >&2
else
  echo "Setting up MCP servers from $MCP_CONFIG_FILE..."

  jq -r '.mcpServers | to_entries[] | @json' "$MCP_CONFIG_FILE" | while IFS= read -r server_json; do
    original_name=$(echo "$server_json" | jq -r '.key')
    server_config=$(echo "$server_json" | jq -c '.value')

    # Sanitize server name: replace non-alphanumeric/underscore/hyphen with underscores
    server_name="${original_name//[^a-zA-Z0-9_-]/_}"

    if claude mcp list 2>/dev/null | grep -q "^${server_name}:"; then
      echo "  MCP server '$server_name' already registered, skipping"
      continue
    fi

    echo "  Adding MCP server: $original_name (as $server_name)"
    if claude mcp add-json --scope user "$server_name" "$server_config"; then
      echo "  ✓ Added $server_name"
    else
      echo "  ✗ Failed to add $server_name" >&2
    fi
  done
fi

# --- Plugins ---

if [[ ! -f "$SETTINGS_FILE" ]]; then
  echo "Warning: settings.json not found at $SETTINGS_FILE, skipping plugin setup" >&2
  exit 0
fi

enabled_plugins=$(jq -r '.enabledPlugins // {} | to_entries[] | select(.value == true) | .key' "$SETTINGS_FILE")

if [[ -z "$enabled_plugins" ]]; then
  echo "No plugins declared in enabledPlugins, skipping plugin setup"
  exit 0
fi

echo "Setting up plugins..."

installed_plugins=$(claude plugin list 2>/dev/null || true)
registered_marketplaces=$(claude plugin marketplace list 2>/dev/null || true)

while IFS= read -r plugin_id; do
  marketplace="${plugin_id##*@}"

  # Check if already installed
  if echo "$installed_plugins" | grep -q "❯ ${plugin_id}"; then
    echo "  Plugin '$plugin_id' already installed, skipping"
    continue
  fi

  # Register marketplace if needed
  if [[ "$marketplace" != "$BUILTIN_MARKETPLACE" ]]; then
    if echo "$registered_marketplaces" | grep -q "❯ ${marketplace}"; then
      echo "  Marketplace '$marketplace' already registered"
    elif [[ -n "${MARKETPLACE_REPOS[$marketplace]+_}" ]]; then
      repo="${MARKETPLACE_REPOS[$marketplace]}"
      echo "  Registering marketplace '$marketplace' from $repo..."
      if claude plugin marketplace add "$repo"; then
        echo "  ✓ Registered marketplace '$marketplace'"
        registered_marketplaces=$(claude plugin marketplace list 2>/dev/null || true)
      else
        echo "  ✗ Failed to register marketplace '$marketplace', skipping plugin '$plugin_id'" >&2
        continue
      fi
    else
      echo "  Warning: unknown marketplace '$marketplace' for plugin '$plugin_id', skipping" >&2
      continue
    fi
  fi

  echo "  Installing plugin: $plugin_id"
  if claude plugin install "$plugin_id"; then
    echo "  ✓ Installed $plugin_id"
  else
    echo "  ✗ Failed to install $plugin_id" >&2
  fi

done <<< "$enabled_plugins"

echo "Claude Code setup complete."
