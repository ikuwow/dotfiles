# Cross-Repository Access

When referencing files or code in a repository other than the current
working directory, prefer local clones over GitHub API access.

## File reading

Delegate to the `cross-repo-reader` subagent. It owns ghq lookup,
optional fast-forward sync, and file reading, and returns a summary
with citations.

Do not pass a `model` parameter when invoking this agent. The
agent's frontmatter sets `model: sonnet` as the default, and the
Agent tool's per-call `model` argument takes precedence over the
frontmatter when supplied. Letting the frontmatter default apply is
how this agent stays on Sonnet without the parent having to
remember the model on every call.

Pass the agent enough context about what to look for and why, so it
can make judgment calls about which files to read.

Exception: when a single specific file path is already known, the
main agent may read it directly via Read/Grep without delegating.

## When to Use GitHub API Instead

Fall back to `gh` commands or GitHub API only for data that does not
exist as local files:

- PR / issue metadata, comments, reviews
- CI check status and logs
- Repository settings, branch protection rules
- Commit comparison across branches not available locally
