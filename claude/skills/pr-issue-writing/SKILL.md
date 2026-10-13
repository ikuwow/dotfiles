---
name: pr-issue-writing
description: Write or edit the title and body of a pull request or an issue, and create either. Carries the preflight that runs before writing one (target repository and its visibility, the repository's own rules and language, its template, a duplicate search), the five properties a PR body is judged against (Decidable, Grounded, Necessary, Scoped, Conformant), the criteria an issue body is judged against, the PR body template, the review a draft body passes against its sources, and the commands for creating a draft PR or an issue and for editing a title or body safely. Invoke before creating a PR or an issue, before writing a PR or issue title or body, including a draft shown in chat for the user to review, before editing one, and when bringing an existing PR into conformance. Invoke it again whenever the target repository differs from the one it last ran for.
---

# Write a Pull Request or Issue

Creating a PR or an issue, and writing or editing its title or body,
runs through this workflow, including a draft shown in chat, since
approving it leads straight to posting it.

## Workflow

Copy this checklist into the assistant message and check off each step
as it completes:

```
- [ ] Step 1: Load the criteria
- [ ] Step 2: Preflight
- [ ] Step 3: Write
- [ ] Step 4: Review
- [ ] Step 5: Send
```

The target's own rules decide the language and format of the title and
body, over the language of the chat, the user's global rules, and the
rules of a working directory that is another repository.

## Step 1: Load the criteria

1. Read [properties.md](properties.md) for a PR, or
   [issue-body.md](issue-body.md) for an issue
   - To only judge a body, judge it against that file and stop here
1. For a new PR, check `gh pr view --json number,url`, and when the
   branch already has one, continue as an edit of it
1. Invoke the `technical-writing` skill

## Step 2: Preflight

Target and Rules carry over from an earlier preflight in the session
for the same target and run again for any other target, since what one
target's rules decide does not carry over to another. Template and
Duplicates run for a create only. The target's own `CLAUDE.md` is not
loaded when it is another repository than the working directory's.

- Target: take `owner/repo` from `-R` / `--repo`, otherwise from the
  working directory, and read the visibility of the target and of the
  repository the content comes from with
  `gh repo view [<owner>/<repo>] --json nameWithOwner,visibility`
  - When the target's visibility is wider (`PRIVATE` to `INTERNAL` or
    `PUBLIC`, `INTERNAL` to `PUBLIC`) and the body will carry anything
    from the source (its `owner/repo`, issue and PR numbers, quoted
    code, comments, or rule text), confirm with the user before
    writing, since everyone the target admits can read it from the
    moment it is created
- Rules: read `CONTRIBUTING.md` at the target's root, in `.github/`, or
  in `docs/`, and when the target is another repository than the
  working directory's, also its root `CLAUDE.md` and `AGENTS.md`
  - Follow what they state about language, title format, labels, and
    linking over this skill's defaults
  - With no language rule there, the criteria file's language rule
    decides
- Template: match file names case-insensitively
  - PR: `pull_request_template.md` at the root, in `docs/`, or in
    `.github/`, and the files in a `PULL_REQUEST_TEMPLATE/` directory
    in any of those three
  - Issue: the `.md` and `.yml` files in `.github/ISSUE_TEMPLATE/`
    other than `config.yml`, taking the one whose purpose matches
    - An issue form (`.yml`) cannot be filled through `--body-file`, so
      its field labels become the section headings, with every
      required field filled
    - In `config.yml`, `blank_issues_enabled: false` means every issue
      starts from a template, and when the request fits a channel in
      `contact_links`, ask the user whether to use it instead
- Duplicates: run
  `gh search issues --repo <owner>/<repo> --include-prs <keywords>`
  with at least two keyword sets, such as the component's name and the
  symptom, leaving `--state` unset so a closed one declined earlier
  surfaces too
  - A duplicate is another issue or PR covering the same problem, or
    for a PR another PR making the same change (the issue a PR
    addresses is its parent)
  - When one turns up, stop and ask the user whether to comment on it,
    create a new one linked to it, or drop it

When the target has no `CONTRIBUTING.md`, `config.yml`, or template of
its own, read the one in the owner's public `.github` repository, which
GitHub serves as the default
([default community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)).
Read a file of another repository from a local clone when
`ghq list -p -e <owner>/<repo>` finds one, through
`git -C <clone> fetch origin` and
`git -C <clone> show origin/HEAD:<path>`, since its working tree may be
stale; otherwise, or when `origin/HEAD` does not resolve, through
`gh api repos/<owner>/<repo>/contents/<path> -H 'Accept: application/vnd.github.raw'`.

Close a preflight that ran by posting in the assistant message the target,
both visibilities, and the language with the file or fallback that
decided it, and, for a create, the template path or the paths searched
and each duplicate query with its hit count, so an absence can be
checked.

## Step 3: Write

1. For an edit, fetch the current body with
   `gh pr view <number> --json body --jq .body` (`gh issue view` for an
   issue)
1. Write the body to a fresh file under the session scratchpad
   directory with the Write tool, a new filename per revision, in the
   language the preflight settled and, for a create, the template it
   found
   - Do not generate a temp filename, and do not Read a file that does
     not exist yet

## Step 4: Review

Check the drafted title and body claim by claim before they are sent or
shown in chat, since an inference written as a sourced fact reaches the
reader unchecked. On an edit, review only the claims the draft adds or
changes.

1. List each claim in the assistant message, including those in
   parentheticals, glosses, table cells, and checklist items, which a
   writer reads as framing rather than claims, with the place it came
   from among what the session has read (an issue, a PR, a file, a
   command's output, the user's statement), marked `sourced` when that
   place states it and `inferred` otherwise
   - A date in a source's title is a date, and reading it as a deadline
     is an inference
   - Classifying an item states the writer's view, and reading a
     decision into it is an inference
   - A tool named in a step the reader is meant to follow
     (verification, rollout, rollback, monitoring) is a claim that the
     project uses it
1. Keep a claim the reader would act on (a deadline, a status, a
   decision and who made it, an owner, a cause) as a fact only when it
   is `sourced`, since these steer how the work is prioritized, and
   write an `inferred` one as the writer's inference with its evidence,
   or drop it
1. For each claim marked unverified, run the check when a source at
   hand settles it (a clone on disk, a file, a command that needs no
   setup) and write the result in place of the label; a check needing a
   new clone, authentication, or a long query leaves the label
1. Check that the title and the whole body are in the language the
   preflight settled

## Step 5: Send

Pass a body through `--body-file` and never `--body`, since the
`#`-prefixed lines a body carries trigger Claude Code's security
pre-check under `--body`, which no hook can bypass. Add
`-R <owner>/<repo>` to each command when the target is another
repository than the working directory's.

- Create a PR, once the branch is pushed:
  `gh pr create --draft --title '...' --body-file <file>`, then display
  the URL from `gh pr view --json url --jq '.url'`
- Create an issue: `gh issue create --title '...' --body-file <file>`,
  and display the URL it prints
- Edit: summarize in the assistant message what is added, removed, or
  reworded, then send the title with `gh pr edit <number> --title '...'`
  and the body with `gh pr edit <number> --body-file <file>`
  (`gh issue edit` for an issue)
