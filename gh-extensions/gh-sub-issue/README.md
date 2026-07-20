# gh-sub-issue

A `gh` CLI extension for listing, adding, and removing GitHub sub-issues,
wrapping the `/issues/{number}/sub_issues` REST endpoints that `gh` has no
built-in subcommand for.

## Installation

From within this directory:

```sh
gh extension install .
```

`gh extension install` only accepts a local repo via the literal `.`
argument, run from inside the extension directory (verified against
cli/cli's `pkg/cmd/extension/command.go`, where the install handler
exact-matches `args[0] == "."`).

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
