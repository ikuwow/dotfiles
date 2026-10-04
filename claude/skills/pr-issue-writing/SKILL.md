---
name: pr-issue-writing
description: Write or edit the title and body of a pull request or an issue, and create either. Carries the five properties a PR body is judged against (Decidable, Grounded, Necessary, Scoped, Conformant), the criteria an issue body is judged against, the PR body template, the review a draft body passes against its sources, and the commands for creating a draft PR or an issue and for editing a title or body safely. Invoke before writing a PR or issue title or body, before editing one, and when bringing an existing PR into conformance.
---

# Write a Pull Request or Issue

Writing or editing the title or body of a PR or an issue runs through
here.

For a PR, read [properties.md](properties.md) for the five properties
its body is judged against and the template to write into. For an
issue, read [issue-body.md](issue-body.md) instead. Invoke the
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
1. Review the draft under "Review a draft against its sources" below,
   writing any revision to a fresh file
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
  1. Review the draft under "Review a draft against its sources" below,
     writing any revision to a fresh file
  1. Execute the edit:
     `gh pr edit <number> --body-file <body file path>`
     (`gh issue edit <number> --body-file <body file path>` for an
     issue)

## Review a draft against its sources

Check a drafted body claim by claim before `gh issue create` or an
edit command sends it, asking of each claim whether a source states it
or the writer inferred it. An inference written as a sourced fact
reaches the reader unchecked, and the reader acts on it.

On an edit, review only the claims the draft adds or changes relative
to the fetched current body, so the cost of a review follows the size
of the edit.

- For each claim under review, including those inside parentheticals,
  glosses, and asides, find the place it came from (an issue, a PR, a
  file, a command's output, a log query, the user's own statement)
  among what the session has already read, and check that the place
  states the claim itself
  - A date in a title states a date, and reading it as a deadline is an
    inference
  - Classifying an item states the writer's view, and reading a
    decision into it is an inference
  - A tool or service named in a step the reader is meant to follow
    (verification, rollout, rollback, monitoring) is a claim that the
    project uses it
- Keep a claim the reader would act on (a deadline, a status, a
  decision and who made it, an owner, a cause) as a fact only when a
  source states it, since these claims steer how the work is
  prioritized
- Write a claim no source states as the writer's inference with the
  evidence that points to it, or drop it
- For each claim the draft marks as unverified or to be confirmed, run
  the check when a source at hand settles it (a clone already on disk, a
  file, a command that runs without setup), and write the result in
  place of the label
  - A label left where such a source settles the claim passes the check
    to every reader
  - A check that needs a new clone, authentication, or a long-running
    query is out of reach, so the label stays
