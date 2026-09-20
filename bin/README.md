# bin/

Custom executable scripts deployed to `~/bin/` via symlinks.

## Scripts

| Script | Description |
| --- | --- |
| `aws-mfa` | Automate AWS session token acquisition via MFA |
| `claude-subagent-models` | Show which model each Claude Code subagent ran on, from session transcripts |
| `install-aimsg-hook.sh` | Symlink `~/.config/git/hooks/prepare-commit-msg` into the current repo's `.git/hooks/` to enable the AI commit-message drafter |
| `git-cleanup-branches` | Delete local branches whose content the default branch holds (merged, squash-merged) and prune stale worktree entries |
| `git-worktree-create` | Create a git worktree under `.worktrees/`. Defaults to branching from `origin/<default>`; pass a second argument to override the base |
| `pipectlx` | PipeCD CLI wrapper that auto-injects API key and server address from config |
| `ssm` | Start an AWS SSM session by instance ID or Name tag |
| `vssh` | SSH into a Vagrant machine using sshrc with auto-generated ssh-config |
