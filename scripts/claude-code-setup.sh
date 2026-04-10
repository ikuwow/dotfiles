#!/usr/bin/env bash

# Claude Code CLI setup: registers MCP servers and installs plugins.
# Safe to run multiple times (idempotent).
# Counterpart to scripts/deploy.sh, which handles file symlinks only.

set -eu

# --- MCP servers ---
# add-json exits 1 if already registered, so suppress with || true
# IDE-local servers (intellij-index, goland-index) are intentionally omitted
claude mcp add-json --scope user deepwiki '{"type":"http","url":"https://mcp.deepwiki.com/mcp"}' || true
claude mcp add-json --scope user Context7 '{"command":"npx","args":["-y","@upstash/context7-mcp"]}' || true

# --- Plugins ---
# marketplace add and plugin install are both idempotent
claude plugin marketplace add openai/codex-plugin-cc
claude plugin install codex@openai-codex
