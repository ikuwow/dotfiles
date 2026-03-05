# bin/

Custom executable scripts deployed to `~/bin/` via symlinks.

## Scripts

| Script | Description |
| --- | --- |
| `aws-mfa` | Automate AWS session token acquisition via MFA |
| `git-ai-commit.sh` | Generate a commit message from staged diff using AI (codex) |
| `git-delete-squashed` | Delete local branches that were squash-merged into the default branch |
| `git-worktree-create` | Create a git worktree with a sanitized directory name under `.worktrees/` |
| `pipectlx` | PipeCD CLI wrapper that auto-injects API key and server address from config |
| `ssm` | Start an AWS SSM session by instance ID or Name tag |
| `vssh` | SSH into a Vagrant machine using sshrc with auto-generated ssh-config |
