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
  server_name=$(echo "$server_json" | jq -r '.key')
  server_command=$(echo "$server_json" | jq -r '.value.command')

  echo "Adding MCP server: $server_name"

  # Build args array
  args_json=$(echo "$server_json" | jq -c '.value.args // []')

  # Convert args array to command line arguments
  args=""
  if [[ "$args_json" != "[]" ]]; then
    args=$(echo "$args_json" | jq -r '.[] | @sh' | tr '\n' ' ')
  fi

  # Execute claude mcp add command
  eval "claude mcp add \"$server_name\" \"$server_command\" $args"

  echo "✓ Added $server_name"
done

echo "All MCP servers have been added successfully!"
