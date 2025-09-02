#!/usr/bin/env bash

set -euo pipefail

MCP_CONFIG_FILE="$HOME/.claude/.mcp.json"

if [[ ! -f "$MCP_CONFIG_FILE" ]]; then
  echo "Error: MCP config file not found at $MCP_CONFIG_FILE" >&2
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed" >&2
  exit 1
fi

if ! command -v claude &> /dev/null; then
  echo "Error: claude CLI is required but not installed" >&2
  exit 1
fi

echo "Adding MCP servers from $MCP_CONFIG_FILE..."

jq -r '.mcpServers | to_entries[] | @json' "$MCP_CONFIG_FILE" | while IFS= read -r server_json; do
  original_name=$(echo "$server_json" | jq -r '.key')
  server_config=$(echo "$server_json" | jq -c '.value')

  # Sanitize server name: replace dots and other invalid characters with underscores
  server_name="${original_name//[^a-zA-Z0-9_-]/_}"

  # Check if server already exists in user scope
  if claude mcp list --scope user 2>/dev/null | grep -q "^$server_name:"; then
    echo "⚠️  MCP server $original_name (as $server_name) already exists in user scope, skipping..."
    continue
  fi

  echo "Adding MCP server: $original_name (as $server_name)"

  # Execute claude mcp add-json command with user scope
  if claude mcp add-json --scope user "$server_name" "$server_config"; then
    echo "✓ Added $original_name as $server_name (user scope)"
  else
    echo "❌ Failed to add $original_name as $server_name" >&2
  fi
done

echo "MCP server configuration completed."
