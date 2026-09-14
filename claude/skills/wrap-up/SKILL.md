---
name: wrap-up
description: Take stock of a session before it ends (unfinished work, state that ending the session discards, and findings recorded nowhere), propose the follow-up actions, run only the ones the user selects, and report whether the session is safe to end.
disable-model-invocation: true
---

# Wrap Up

This skill brings a session to a state where ending it loses nothing the
user needs. Reading runs on its own. Every write, local ones included,
runs only after the user selects it, since one wrap-up can touch several
repositories and PRs and the user approves exactly the operations and
text they were shown.

## Step 1: Inventory

Collect items with read-only commands and from the conversation. Skip a
source whose precondition is absent: the git checks outside a git
repository, the PR checks when the session touched no PR.

- Git, for every repository this session worked in
  - `git status --short`
  - `git stash list`
  - `git log --branches --not --remotes --oneline` for commits no remote has
  - `git worktree list`
  - the current branch
- PRs this session created or updated
  - `gh pr view <number> --json state,isDraft,statusCheckRollup,reviewDecision`
  - review threads with no reply
- Work that stops when the session ends
  - background shells, Monitors, and subagents started in this session
  - session crons, listed by `CronList`
  - artifact watches, listed by the `Artifact` tool's `status` action
- The conversation
  - work the session said it would do and did not start
  - questions put to the user that have no answer yet
  - decisions and investigation results that no repository file, issue, or PR holds
- Content that exists only in the scratchpad

Attribute each uncommitted change before listing it, and list only the
changes this session made. Another concurrent session may share the
working tree, and committing its edits would ship them under this
session's intent.

## Step 2: Propose

Turn each item that needs action into one proposal, and run nothing in
this step.

- Each proposal names the operation (commit, push, create an issue, comment on a PR, stop a task, delete a branch, and so on)
- Each proposal names its target: the repository, branch, and PR or issue number
- A write that carries text includes the full draft of that text (commit message, issue body, comment)

A record goes where a later reader will look for it.

- A fact about a PR's change goes in that PR's body or in a comment on it, where the reviewer of that change reads it
- Unfinished work and investigation results not tied to a PR go in a new issue in the repository the work belongs to, where a later search of that repository finds them
- Scratchpad content is written into the issue or PR itself
  - A file path is not a record, because nobody looks in a place they do not remember

Draft issue and PR text with the `pr-issue-writing` skill, and any other
prose longer than a sentence with the `technical-writing` skill.

- Uncommitted changes on the default branch get a proposal to create a branch and commit there
- A branch whose PR is merged gets a proposal to run `git cleanup`
- An item that needs no action gets no proposal, and counts toward the report

## Step 3: Select

When there are no proposals, go to Step 5.

1. Show every proposal in the conversation, numbered, with its draft in full
1. Ask with AskUserQuestion, multiSelect, one option per proposal labeled with its number
   - A question holds at most 4 options, so split the proposals across questions, and across calls past 4 questions
1. Treat an unselected proposal as declined, and follow any free-text answer as written

## Step 4: Execute

Run the selected proposals as drafted. When a proposal cannot run as
shown (a command fails, or the target has changed), stop that proposal
and carry it to the report rather than running a version the user did
not see.

## Step 5: Retro note

Invoke the `retro-note` skill. Its append to the local log follows its
own contract and needs no selection in Step 3.

## Step 6: Report

1. Open with the verdict
   - Safe to end: every proposal ran or was declined, and every unresolved item is recorded in an issue or PR
   - Items remain: otherwise
1. Give the retro-note result (finding count and path) in one line, so a later end-of-session message in the same session finds the note already recorded
1. For each declined or failed proposal and each unresolved item, write one line naming where it now lives (PR or issue URL) or what ending the session discards or stops
1. Give the count of items that needed no action
