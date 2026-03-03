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

Spec: https://docs.anthropic.com/en/docs/claude-code/hooks (PermissionRequest section)
"""
import json
import sys

APPROVED_PREFIXES = (
    "git commit",
    "gh pr create",
)


def should_approve(tool_name: str, command: str) -> bool:
    """Return True if the permission request should be auto-approved.

    >>> should_approve("Bash", "git commit -m 'fix'")
    True
    >>> should_approve("Bash", "git commit -m '$(cat <<\\'EOF\\'\\nmsg\\nEOF)'")
    True
    >>> should_approve("Bash", "git commit -m 'Subject' -m '' -m 'Co-authored-by: X'")
    True
    >>> should_approve("Bash", "  git commit -m 'leading whitespace'")
    True
    >>> should_approve("Bash", "gh pr create --draft --title 't' --body 'b'")
    True
    >>> should_approve("Bash", "git push origin main")
    False
    >>> should_approve("Bash", "git rebase main")
    False
    >>> should_approve("Bash", "gh pr edit 123 --title 'new'")
    False
    >>> should_approve("Edit", "git commit -m 'wrong tool'")
    False
    """
    if tool_name != "Bash":
        return False
    return command.lstrip().startswith(APPROVED_PREFIXES)


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    if should_approve(
        data.get("tool_name", ""),
        data.get("tool_input", {}).get("command", ""),
    ):
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {"behavior": "allow"}
            }
        }))

    sys.exit(0)
