---
name: pr-issue-writing
description: Write or edit the title and body of a pull request or an issue, and create either. Carries the five properties a body is judged against (Decidable, Grounded, Necessary, Scoped, Conformant) and which of them an issue body is held to, the PR body template, and the commands for creating a draft PR or an issue and for editing a title or body safely. Invoke before writing a PR or issue title or body, before editing one, and when bringing an existing PR into conformance.
---

# Write a Pull Request or Issue

Writing or editing the title or body of a PR or an issue runs through
here.

Read [properties.md](properties.md) for the five properties a body is
judged against and the template to write into. Invoke the
`technical-writing` skill for how the prose itself is built.

Pass a body through `--body-file` and never `--body`, on creation and on
every edit after it. The `#`-prefixed lines a body carries trigger
Claude Code's security pre-check when passed via `--body`, which no hook
can bypass.

## Create a PR

The branch exists, carries the commits, and is pushed before this runs.

1. If the branch already has a PR (`gh pr view --json number,url`),
   skip creation, bring its title and body into conformance using the
   update procedure below, display the PR URL, and stop here
1. Write the body to a fresh file under the session scratchpad
   directory using the Write tool, a new filename per revision. Do not
   generate a temp filename, and do not Read a file that does not exist
   yet
   - Follow the repository's PR template when one exists
1. Create the PR as a draft:
   `gh pr create --draft --body-file <body file path>`
1. Display the PR URL: `gh pr view --json url --jq '.url'`

## Create an issue

1. Write the body to a fresh file under the session scratchpad
   directory using the Write tool, a new filename per revision. Do not
   generate a temp filename, and do not Read a file that does not exist
   yet
   - Follow the repository's issue template when one exists
1. Create the issue:
   `gh issue create --title '...' --body-file <body file path>`
1. Display the issue URL, which `gh issue create` prints to stdout

## Update an existing title or body

Summarize the change in the assistant message body before either edit
below, as a short list of what is being added, removed, or reworded
rather than the full before-and-after.

- Update a title: `gh pr edit <number> --title '...'`
  (`gh issue edit <number> --title '...'` for an issue)
- Update a body:
  1. Fetch the current one:
     `gh pr view <number> --json body --jq .body`
     (`gh issue view <number> --json body --jq .body` for an issue)
  1. Write the new body to a fresh file under the session scratchpad
     directory using the Write tool, a new filename per revision. Do
     not generate a temp filename, and do not Read a file that does not
     exist yet
  1. Execute the edit:
     `gh pr edit <number> --body-file <body file path>`
     (`gh issue edit <number> --body-file <body file path>` for an
     issue)
