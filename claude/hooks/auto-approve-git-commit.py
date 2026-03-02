#!/usr/bin/env python3
"""Auto-approve git commit permission requests for Claude Code."""
import json
import sys

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

if data.get("tool_name") == "Bash":
    command = data.get("tool_input", {}).get("command", "").lstrip()
    if command.startswith("git commit"):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "allow"}
            }
        }))

sys.exit(0)
