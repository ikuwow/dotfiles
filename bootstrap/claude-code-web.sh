#!/bin/bash

# Bootstrap for Claude Code web remote environments (Ubuntu 24.04).
# Installs useful packages, deploys dotfile symlinks, and configures
# Claude Code MCP servers and plugins.

set -eu

echo "Claude Code web remote bootstrap"

# Install packages not in the default image
apt-get update -qq || true
apt-get install -y -qq gh jq fzf shellcheck

# Deploy dotfile symlinks
scripts/deploy.sh

# Claude Code's Bash tool exports the CLI process's own PATH after sourcing
# .bash_profile, so the ~/bin entry .bash_profile adds never reaches it.
# ~/.local/bin is on that PATH in the default image.
mkdir -p "$HOME/.local/bin"
find "$HOME/bin/" -maxdepth 1 -type l -exec ln -fns {} "$HOME/.local/bin/" \;

# Register MCP servers and install plugins
# (user-level .mcp.json and enabledPlugins are not applied automatically in remote sessions)
scripts/claude-code-setup.sh

echo "Claude Code web remote bootstrap complete."
