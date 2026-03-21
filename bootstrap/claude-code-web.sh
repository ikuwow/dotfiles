#!/bin/bash

# Bootstrap for Claude Code web remote environments (Ubuntu 24.04).
# Installs useful packages, deploys dotfile symlinks, and configures
# Claude Code MCP servers.

set -eu

echo "Claude Code web remote bootstrap"

# Install packages not in the default image
apt-get update -qq || true
apt-get install -y -qq gh jq fzf

# Deploy dotfile symlinks
scripts/deploy.sh

# Register MCP servers (user-level .mcp.json is not read in remote sessions)
claude mcp add --transport http deepwiki https://mcp.deepwiki.com/mcp
claude mcp add Context7 -- npx -y @upstash/context7-mcp

echo "Claude Code web remote bootstrap complete."
