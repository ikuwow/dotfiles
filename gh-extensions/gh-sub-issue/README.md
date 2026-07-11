# gh-sub-issue

A `gh` CLI extension for listing, adding, and removing GitHub sub-issues,
wrapping the `/issues/{number}/sub_issues` REST endpoints that `gh` has no
built-in subcommand for.

## Installation

Installed automatically by this repo's `scripts/deploy.sh`, which registers
every directory under `gh-extensions/` with `gh extension install`. No manual
step is needed once the dotfiles are deployed.

## Usage

```sh
# List the sub-issues of issue #123
gh sub-issue list 123

# Add issue #456 as a sub-issue of #123
gh sub-issue add 123 --sub-issue-number 456

# Add issue #456 as a sub-issue of #123, replacing its current parent
gh sub-issue add 123 --sub-issue-number 456 --replace-parent

# Remove issue #456 from #123's sub-issues
gh sub-issue remove 123 --sub-issue-number 456
```

## Notes

This is an independent implementation written for this repo; it does not
share code with any upstream `gh-sub-issue` extension.
