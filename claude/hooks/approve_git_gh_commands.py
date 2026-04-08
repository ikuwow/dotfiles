#!/usr/bin/env python3
"""Auto-approve git/gh commands whose command substitution is safe.

Claude Code's security pre-checks flag commands containing backticks,
$(), heredocs, and multiline strings — even when they appear inside
single-quoted strings where the shell will NOT expand them.

This hook auto-approves git commit, gh pr create, and gh issue create
commands when all command substitution ($() or backticks) is inside
single-quoted strings (i.e. safe / not expanded by the shell).

Spec: https://code.claude.com/docs/en/hooks
"""
import sys

from hook_utils import approve_and_exit, has_unsafe_substitution, read_hook_input

APPROVED_PREFIXES = (
    "git commit",
    "gh pr create",
    "gh issue create",
)


def should_approve(tool_name: str, command: str) -> bool:
    """Return True if the command should be auto-approved.

    >>> should_approve("Bash", "git commit -m 'fix: resolve `encoding` issue'")
    True
    >>> should_approve("Bash", "gh pr create --draft --title 'title' --body '## Summary\\n`code`'")
    True
    >>> should_approve("Bash", "gh issue create --title 'title' --body 'body'")
    True
    >>> should_approve("Bash", "git commit -m \\"$(evil)\\"")
    False
    >>> should_approve("Bash", "git push origin main")
    False
    >>> should_approve("Edit", "git commit -m 'wrong tool'")
    False
    """
    if tool_name != "Bash":
        return False
    stripped = command.lstrip()
    if not stripped.startswith(APPROVED_PREFIXES):
        return False
    if has_unsafe_substitution(stripped):
        return False
    return True


if __name__ == "__main__":
    tool_name, command = read_hook_input()
    if tool_name and should_approve(tool_name, command):
        approve_and_exit()
    sys.exit(0)
