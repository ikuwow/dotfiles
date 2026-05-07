# Cross-Repository Access

When referencing files or code in a repository other than the current
working directory, prefer local clones over GitHub API access.

## File reading

Delegate to the `cross-repo-reader` subagent. It owns ghq lookup,
optional fast-forward sync, and file reading via Read/Grep/Glob, and
returns a summary with citations. The agent's frontmatter pins
`model: sonnet`, so the model is enforced regardless of how the
parent calls it.

Pass the agent enough context about what to look for and why, so it
can make judgment calls about which files to read.

Exception: when a single specific file path is already known and the
content is small, the main agent may read it directly via Read/Grep
without delegating.

## When to Use GitHub API Instead

Fall back to `gh` commands or GitHub API only for data that does not
exist as local files:

- PR / issue metadata, comments, reviews
- CI check status and logs
- Repository settings, branch protection rules
- Commit comparison across branches not available locally
