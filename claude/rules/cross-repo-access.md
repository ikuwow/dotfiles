# Cross-Repository Access

When referencing files or code in a repository other than the current
working directory, prefer local clones over GitHub API access.

## Lookup Order

1. Check if the repo is already cloned locally:
   `ghq list | grep <owner>/<repo>`
2. If found, the path is: `/Users/ikuwow/ghq/github.com/<owner>/<repo>`
3. If not found, clone it via SSH: `ghq get -p <owner>/<repo>`
   - Do not clone known-huge repositories (linux, chromium, webkit, etc.)
     without user confirmation
4. Before reading, sync the default branch if it is checked out and clean:
   `git -C <path> pull --ff-only`
   - Only pull when the current branch is the default branch (main/master)
     and there are no unpushed or uncommitted changes
   - If --ff-only fails, do not force — proceed with the existing state
5. Read files locally using Read/Grep/Glob tools with the ghq path

## When to Use GitHub API Instead

Fall back to `gh` commands or GitHub API only for data that does not exist
as local files:

- PR / issue metadata, comments, reviews
- CI check status and logs
- Repository settings, branch protection rules
- Commit comparison across branches not available locally

## Subagent Delegation

Delegate cross-repo reading to a subagent (general-purpose, model: sonnet)
to keep the main conversation context clean.

- The subagent should handle: ghq lookup, pull, file reading, and
  returning a summary of findings
- Exception: if only a single specific file path is needed and already
  known, the main agent may read it directly
- Pass the subagent enough context about what to look for and why,
  so it can make judgment calls about which files to read
