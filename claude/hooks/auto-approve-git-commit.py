#!/usr/bin/env python3
"""Auto-approve permission requests for safe write commands."""
import json
import sys

APPROVED_PREFIXES = (
    "git commit",
    "gh pr create",
)

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, ValueError):
    sys.exit(0)

if data.get("tool_name") == "Bash":
    command = data.get("tool_input", {}).get("command", "").lstrip()
    if command.startswith(APPROVED_PREFIXES):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "allow"}
            }
        }))

sys.exit(0)
