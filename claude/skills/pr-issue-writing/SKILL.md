---
name: pr-issue-writing
description: Write or edit the title and body of a pull request or an issue, and create either. Carries the checks that run before creating one (target repository and its visibility, the repository's own rules, its template, a duplicate search), the five properties a PR body is judged against (Decidable, Grounded, Necessary, Scoped, Conformant), the criteria an issue body is judged against, the PR body template, the review a draft body passes against its sources, and the commands for creating a draft PR or an issue and for editing a title or body safely. Invoke before creating a PR or an issue, before writing a PR or issue title or body, including a draft shown in chat for the user to review, before editing one, and when bringing an existing PR into conformance. Invoke it again whenever the target repository differs from the one it last ran for.
---

# Write a Pull Request or Issue

Creating a PR or an issue, and writing or editing its title or body,
runs through here. So does a draft shown in chat for the user to
review, since approving that draft leads straight to posting it.

The criteria a PR body is judged against, with the template to write
into, are in [properties.md](properties.md), and those for an issue
are in [issue-body.md](issue-body.md). Each procedure below reads its
file as its first step. Invoke the `technical-writing` skill for how
the prose itself is built.

## Target profile

Every create and every edit writes for one target repository, and the
target's own rules decide the language and format of its title and
body. The language of the chat, the rules loaded from the user's global
configuration, and the working directory's `CLAUDE.md` and `AGENTS.md`
do not decide them when the target is another repository.

Before writing a title or body, post the target profile in the
assistant message:

- Repository: the `owner/repo` the PR or issue goes to
- Visibility: the target's, and the source repository's when the body
  carries content from it
- Language: the language, with the file that decides it
  - The target's own `CLAUDE.md`, `AGENTS.md`, or `CONTRIBUTING.md`
    decides when it states one, otherwise English for an open-source
    repository, otherwise the language of the target's existing PRs,
    commits, or issues
- Template: the path found, or the paths searched when none exists
  (create only)
- Duplicates: the queries run and the hits for each (create only)

The steps in [preflight.md](preflight.md) fill the profile: steps 1
and 2 for every create and edit, steps 3 and 4 for a create only.

Build the profile again whenever the target differs from the one the
session's last profile named, since what one repository's rules decide
does not carry over to another. A profile built under an earlier
invocation of this skill covers only its own target.

When this skill is invoked to judge a body rather than to write one,
reading the criteria file is the whole of it, and the procedures below
do not run.

Pass a body through `--body-file` and never `--body`, on creation and on
every edit after it. The `#`-prefixed lines a body carries trigger
Claude Code's security pre-check when passed via `--body`, which no hook
can bypass.

## Create a PR

The branch exists, carries the commits, and is pushed before the steps
below run.

When the PR will be opened by the `implementer` subagent, the parent
runs only [preflight.md](preflight.md) and posts the target profile,
before dispatching it. The implementer opens the PR without this skill,
and the parent later replaces the placeholder body through step 2
below.

1. Read [properties.md](properties.md)
1. If the branch already has a PR (`gh pr view --json number,url`),
   skip creation, bring its title and body into conformance using the
   update procedure below, display the PR URL, and stop here
1. Run the steps in [preflight.md](preflight.md) and post the target
   profile
1. Write the body to a fresh file under the session scratchpad
   directory using the Write tool, a new filename per revision. Do not
   generate a temp filename, and do not Read a file that does not exist
   yet
   - Follow the template and the language the profile names
1. Review the draft under "Review a draft against its sources" below,
   writing any revision to a fresh file
1. Create the PR as a draft:
   `gh pr create --draft --title '...' --body-file <body file path>`
1. Display the PR URL: `gh pr view --json url --jq '.url'`

## Create an issue

1. Read [issue-body.md](issue-body.md)
1. Run the steps in [preflight.md](preflight.md) and post the target
   profile
1. Write the body to a fresh file under the session scratchpad
   directory using the Write tool, a new filename per revision. Do not
   generate a temp filename, and do not Read a file that does not exist
   yet
   - Follow the template and the language the profile names
1. Review the draft under "Review a draft against its sources" below,
   writing any revision to a fresh file
1. Create the issue:
   `gh issue create --title '...' --body-file <body file path>`
1. Display the issue URL, which `gh issue create` prints to stdout

## Update an existing title or body

Before either edit below, read [properties.md](properties.md) for a PR
or [issue-body.md](issue-body.md) for an issue, and post the target
profile from steps 1 and 2 of [preflight.md](preflight.md) unless the
session's last profile names the same target. Then summarize the change
in the assistant message body, as a short list of what is being added,
removed, or reworded rather than the full before-and-after.

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
     - Follow the language the profile names, and the template the
       preflight found when step 3 ran
  1. Review the draft under "Review a draft against its sources" below,
     writing any revision to a fresh file
  1. Execute the edit:
     `gh pr edit <number> --body-file <body file path>`
     (`gh issue edit <number> --body-file <body file path>` for an
     issue)

## Review a draft against its sources

Check a drafted body claim by claim before a create or edit command
sends it, and before a draft is shown in chat, asking of each claim
whether a source states it or the writer inferred it. An inference
written as a sourced fact reaches the reader unchecked, and the reader
acts on it.

On an edit, review only the claims the draft adds or changes relative
to the fetched current body, so the cost of a review follows the size
of the edit.

1. List in the assistant message each claim under review, including
   those inside parentheticals, glosses, asides, table cells, and
   checklist items, and pair each with the place it came from (an
   issue, a PR, a file, a command's output, a log query, the user's own
   statement) among what the session has already read
   - Mark each claim `sourced` when that place states the claim itself,
     and `inferred` otherwise
   - A date in a source's title (an issue, a ticket) states a date, and
     reading it as a deadline is an inference
   - Classifying an item states the writer's view, and reading a
     decision into it is an inference
   - A tool or service named in a step the reader is meant to follow
     (verification, rollout, rollback, monitoring) is a claim that the
     project uses it
   - The writer reads a gloss or a parenthetical as framing rather
     than as a claim, so listing every claim is what brings those under
     the check
1. Keep a claim the reader would act on (a deadline, a status, a
   decision and who made it, an owner, a cause) as a fact only when it
   is `sourced`, since these claims steer how the work is prioritized
1. Write an `inferred` claim as the writer's inference with the
   evidence that points to it, or drop it
1. For each claim the draft marks as unverified or to be confirmed, run
   the check when a source at hand settles it (a clone already on disk,
   a file, a command that runs without setup), and write the result in
   place of the label
   - A label left where such a source settles the claim passes the
     check to every reader
   - A check that needs a new clone, authentication, or a long-running
     query is out of reach, so the label stays
1. Check that the title and the body are written in the language the
   target profile names, and rewrite them in it when they are not
