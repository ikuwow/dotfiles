#!/usr/bin/env python3
"""Auto-approve permission requests for safe write commands.

Background:
  Even with `Bash(git *)` in the allow list, certain git commit patterns
  trigger permission prompts due to security pre-checks that run before
  allow/deny rule matching:

    - `git commit -m "$(cat <<'EOF' ...)"` -> "Command contains $() command substitution"
    - `git commit -F - <<'EOF' ...`        -> heredoc pattern not matched
    - `git commit -m "msg" -m "" -m "..."`  -> "Command contains empty quotes before dash"

  Similarly, `gh pr create` with a multiline --body (heredoc / $()) triggers the same checks.

  This hook fires via the PermissionRequest event and auto-approves these commands,
  bypassing the pre-checks while keeping other commands subject to normal rules.
"""
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
