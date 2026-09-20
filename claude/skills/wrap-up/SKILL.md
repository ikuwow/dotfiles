---
name: wrap-up
description: Take stock of a session before it ends (unfinished work, state that ending the session discards, and findings recorded nowhere), clear the routine cleanup, propose the writes the user decides on, and report whether the session is safe to end. Trigger when the user signals that the session or the task is over ("終わり", "done", "これで完了", "おつかれ"), when they ask what is left before quitting, and when they invoke /wrap-up.
---

# Wrap Up

This skill brings a session to a state where ending it loses nothing the
user needs. Reading and routine cleanup run on their own. A write the
user decides on runs only after they select it, since one wrap-up can
touch several repositories and PRs and the user approves exactly the
operations and text they were shown. Step 2 draws the line between the
two.

## Step 1: Inventory

Collect items with read-only commands and from the conversation. Skip a
source whose precondition is absent: the git checks when the session
worked in no git repository, the PR checks when it touched no PR, and a
tool-based listing when this session lacks that tool.

- Git, run as `git -C <path>` in every repository and worktree this session worked in
  - `git status --short`
  - `git stash list`
  - `git log --branches --not --remotes --oneline` for local-branch commits that no remote-tracking ref contains as of the last fetch
  - `git worktree list`
  - the current branch
- PRs this session created or updated
  - `gh pr view <number> --repo <owner>/<repo> --json state,isDraft,statusCheckRollup,reviewDecision`
  - unresolved review threads, listed by `gh pr-review review view -R <owner>/<repo> <number> --unresolved --not_outdated`
- Work that runs only while this session is open
  - background shells, Monitors, and subagents this session started, identified from its own `run_in_background`, Monitor, and Agent calls
  - session crons, listed by `CronList`
  - artifact watches, listed by the `Artifact` tool's `status` action
- The conversation
  - work the session said it would do and did not start
  - questions put to the user that have no answer yet
  - decisions and investigation results that no repository file, issue, or PR holds
- Findings that exist only in scratchpad content

Attribute each uncommitted change and stash entry before listing it, and
list only those this session made. Another concurrent session may share
the working tree and the stash, and committing its edits would ship them
under this session's intent.

## Step 2: Sort into cleanup and proposals

Sort each item that needs action into routine cleanup or a proposal. An
item already safe to leave (pushed, recorded in an issue or PR, or
finished) gets neither and is counted in the report.

Routine cleanup removes local state whose content exists somewhere the
user can still reach. Run each cleanup operation here, as it is sorted,
and carry the result to the report. Naming one before the selection
would put it in front of the user as something to read and weigh, which
is the cost this class exists to remove.

Where the worst case of a local cleanup is that the user reruns a
command, it belongs in this class. Sorting such an item into a proposal
costs the user a decision to buy back state they can recreate, so the
doubtful local cleanup runs and appears in the report.

- Local branches whose content the default branch already holds, and the worktrees attached to them, removed by `git cleanup` run from the root worktree of each repository this session worked in
  - `git cleanup` decides each branch on its own content, deletes none while the working tree has uncommitted changes, and leaves a worktree it cannot remove without `--force`, so the run needs no per-branch gate from this skill
  - It starts by checking out the default branch, which fails inside a linked worktree and, in the root worktree, moves the session off the branch it was on, so the report names the switch alongside the branches removed
- A background shell, Monitor, subagent, session cron, or artifact watch this session started whose result the session has already reported

Everything else is a proposal: a write to a repository or to GitHub, a
removal of content held nowhere else (uncommitted changes, a stash
entry, an unpushed commit, a finding that lives only in scratchpad
content), and an operation on state another session created. A proposal
that holds local state keeps it: `git cleanup` deletes nothing while the
working tree is dirty, and it spares a branch whose content the default
branch lacks.

- Each proposal names the operation (commit, push, create an issue, comment on a PR, stop a task whose result is recorded nowhere, delete a branch whose PR is not merged, and so on)
- Each proposal names its target: the repository, branch, and PR or issue number
- A write that carries text includes the full draft of that text (title, body, comment, commit message)
- A proposal that needs another to run first names that proposal, as a push names the commit it pushes

A record goes where a later reader will look for it.

- A fact about a PR's change goes in that PR's body when it changes what the reviewer decides, and in a comment on the PR otherwise
- Unfinished work and investigation results not tied to a PR go in a comment on the open issue already tracking that work, or else in a new issue in the repository the work belongs to
  - A defect this session introduced, in a change of its own already merged, is proposed as the fix: a branch, the edit, and a commit, ending there, with the edit and the commit message as the proposal's draft
    - That proposal's question offers the issue as its other option, so a declined fix still leaves the defect recorded
    - An issue carries the defect on its own when the session cannot fix it that way
- Findings from scratchpad content are written into the issue or PR itself
  - A file path is not a record, because nobody looks in a place they do not remember

Draft issue and PR titles and bodies against the `pr-issue-writing`
skill, and comments, commit message bodies, and other prose longer than
a sentence with the `technical-writing` skill. This step takes only
their writing criteria: the commands that create or edit an issue or PR
run in Step 4, for a selected proposal.

Local git proposals keep to what the session changed.

- A commit proposal names the exact paths it stages, and stages them by path rather than with `git add -A` or `git commit -a`, so another session's changes stay out of it
- Uncommitted changes on the default branch get a proposal to create a branch and commit there

## Step 3: Select

When there are no proposals, go to Step 5, where the cleanup Step 2 already ran is reported.

1. Show every proposal in the conversation, numbered, with its draft in full
1. Ask with AskUserQuestion, multiSelect, with each option labeled by its proposal number
   - Each question takes 2 to 4 options and each call 1 to 4 questions, so group the proposals 2 to 4 per question (5 as 3 and 2), using further calls past 4 questions
   - Ask a single proposal as a single-select question with the options run and skip
1. Treat an unselected proposal as declined
   - When a free-text answer changes a draft or asks for another operation, show the revised proposals and ask again before Step 4

## Step 4: Execute

Run the selected proposals as drafted. Each proposal ends at the last
operation it names, so a commit proposal stops at the commit, without a
push, a PR, or a CI watch that no selected proposal names.

When a proposal cannot run as shown (a command fails, or the target has
changed), stop it and every selected proposal that needs it, and carry
them to the report with the steps that already ran, rather than running
a version the user did not see.

## Step 5: Report

1. Open with the verdict
   - Safe to end: the routine cleanup and every selected proposal ran
   - Items remain: a cleanup operation failed in Step 2, or a selected proposal failed or was stopped in Step 4
1. List the routine cleanup that ran, one line per operation
1. For each declined, failed, or stopped item, write one line naming where it now lives: a PR or issue URL, a place that exists only on this machine (uncommitted changes, a stash entry, or an unpushed branch, with its repository), or what ending the session stops or discards
1. Give the count of items already safe to leave
