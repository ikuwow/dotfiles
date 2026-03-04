#!/usr/bin/env python3
"""Auto-approve commands that use heredocs but not command substitution.

Background:
  Claude Code's security pre-checks flag heredoc patterns (<<EOF, <<'EOF')
  even when they are safe. Commands like:

    git commit -F /dev/stdin <<'EOF'
    message
    EOF

  are safe because single-quoted heredocs do not expand variables or run
  command substitution. This hook auto-approves such commands while
  explicitly rejecting any that contain $() or backtick substitution.

Spec: https://docs.anthropic.com/en/docs/claude-code/hooks (PermissionRequest section)
"""
import json
import re
import sys

APPROVED_PREFIXES = (
    "git commit",
    "gh pr create",
    "gh issue create",
)

# Match $( or backtick outside of single-quoted heredoc body.
# We only check the command portion before the heredoc delimiter.
COMMAND_SUBSTITUTION_RE = re.compile(r"\$\(|`")


def should_approve(tool_name: str, command: str) -> bool:
    """Return True if the permission request should be auto-approved.

    Safe heredoc patterns are approved:
    >>> should_approve("Bash", "git commit -F /dev/stdin <<'EOF'\\nmsg\\nEOF")
    True
    >>> should_approve("Bash", 'git commit -F /dev/stdin <<"EOF"\\nmsg\\nEOF')
    True
    >>> should_approve("Bash", "git commit -F /dev/stdin <<EOF\\nmsg\\nEOF")
    True
    >>> should_approve("Bash", "gh pr create --title 't' --body-file /dev/stdin <<'EOF'\\nb\\nEOF")
    True
    >>> should_approve("Bash", "gh issue create --title 't' --body-file /dev/stdin <<'EOF'\\nb\\nEOF")
    True

    Commands with command substitution are rejected:
    >>> should_approve("Bash", "git commit -m \\"$(cat <<'EOF'\\nmsg\\nEOF)\\"")
    False
    >>> should_approve("Bash", "git commit -m \\"`date`\\"")
    False
    >>> should_approve("Bash", "gh pr create --body \\"$(cat body)\\"")
    False

    Non-matching commands are not approved:
    >>> should_approve("Bash", "git push origin main")
    False
    >>> should_approve("Bash", "rm -rf /")
    False
    >>> should_approve("Edit", "git commit -F /dev/stdin <<'EOF'\\nmsg\\nEOF")
    False

    Commands without heredoc are not approved (no need - they pass normal checks):
    >>> should_approve("Bash", "git commit -m 'simple message'")
    False
    """
    if tool_name != "Bash":
        return False

    stripped = command.lstrip()
    if not stripped.startswith(APPROVED_PREFIXES):
        return False

    # Extract the command portion before the heredoc body starts.
    # The heredoc delimiter line is the first line; body follows.
    first_line = stripped.split("\n", 1)[0]

    # Reject if command substitution is present anywhere in the command
    if COMMAND_SUBSTITUTION_RE.search(command):
        return False

    # Only approve if a heredoc is actually used (that's what triggers the check)
    if "<<" not in first_line:
        return False

    return True


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
