#!/usr/bin/env python3
"""Auto-approve read-only gh api graphql queries.

gh api graphql requires -f query='...' which triggers the ask rule
"Bash(gh api * -f *)". This hook selectively overrides that for
read-only queries (query/shorthand), while mutations stay gated.

Convention (see claude/rules/gh-graphql.md): read-only GraphQL must
use single-quoted -f query='query ...' or -f query='{ ... }'.

Spec: https://code.claude.com/docs/en/hooks
"""
import re
import sys

from hook_utils import approve_and_exit, has_unsafe_substitution, read_hook_input

GRAPHQL_QUERY_RE = re.compile(r"-f\s+query='([^']*)'")


def should_approve(tool_name: str, command: str) -> bool:
    """Return True if the command is a read-only gh api graphql call.

    Read-only queries:
    >>> should_approve("Bash", "gh api graphql -f query='query { viewer { login } }'")
    True
    >>> should_approve("Bash", "gh api graphql -f query='{ viewer { login } }'")
    True
    >>> should_approve("Bash", "gh api graphql -f query='  query { viewer { login } }'")
    True
    >>> should_approve("Bash", "gh api graphql -f query='query($o: String!) { repository(owner: $o) { name } }' -f owner='octocat'")
    True

    Mutations (must remain in ask):
    >>> should_approve("Bash", "gh api graphql -f query='mutation { addStar(input: {starrableId: 123}) { clientMutationId } }'")
    False

    Multiple query= flags (last one wins, must also be read-only):
    >>> should_approve("Bash", "gh api graphql -f query='query { safe }' -f query='mutation { evil }'")
    False
    >>> should_approve("Bash", "gh api graphql -f query='mutation { evil }' -f query='query { safe }'")
    True

    Non-matching formats (fall through to ask):
    >>> should_approve("Bash", "gh api graphql --field query='query { viewer { login } }'")
    False
    >>> should_approve("Bash", "gh api graphql -f query=\\"query { viewer { login } }\\"")
    False
    >>> should_approve("Bash", "gh api /repos/owner/repo -f title='hello'")
    False

    Unsafe substitution outside single quotes:
    >>> should_approve("Bash", "gh api graphql -f query='query { viewer }' -f x=$(evil)")
    False

    Wrong tool:
    >>> should_approve("Edit", "gh api graphql -f query='query { viewer }'")
    False
    """
    if tool_name != "Bash":
        return False
    stripped = command.lstrip()
    if not stripped.startswith("gh api graphql"):
        return False
    if has_unsafe_substitution(stripped):
        return False
    matches = GRAPHQL_QUERY_RE.findall(stripped)
    if not matches:
        return False
    # Use the last match — gh uses the last -f value when duplicated
    query_body = matches[-1].lstrip()
    return query_body.startswith("query") or query_body.startswith("{")


if __name__ == "__main__":
    tool_name, command = read_hook_input()
    if tool_name and should_approve(tool_name, command):
        approve_and_exit()
    sys.exit(0)
