---
name: wrap-up
description: Take stock of a session before it ends (unfinished work, state that ending the session discards, and findings recorded nowhere), describe each serious failure in how the agent worked with its risk and the directions a fix could take, clear the routine cleanup, propose the writes the user decides on, and report whether the session is safe to end. Trigger when the user signals that the session or the task is over ("終わり", "done", "これで完了", "おつかれ"), when they ask what is left before quitting, and when they invoke /wrap-up.
---

# Wrap Up

This skill brings a session to a state where ending it loses nothing the
user needs. Reading and routine cleanup run on their own, since
neither writes to a repository or GitHub, the targets Step 2 holds for
the user's selection, apart from closing a settled issue. A write the
user decides on runs only after they select it, since one wrap-up can
touch several repositories and PRs and the user approves exactly the
operations and text they were shown. Step 2 draws the line between the
two.

## Step 1: Inventory

Collect the items with read-only commands and from the conversation. Skip a
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
- Open issues that those PRs address or that the user named as the work target, read with `gh issue view <number> --repo <owner>/<repo>`
- Work that runs only while this session is open
  - background shells, Monitors, and subagents this session started, identified from its own `run_in_background`, Monitor, and Agent calls
  - session crons, listed by `CronList`
  - artifact watches, listed by the `Artifact` tool's `status` action
- The conversation
  - work the session said it would do and did not start
  - questions put to the user that have no answer yet
  - decisions and investigation results that no repository file, issue, or PR holds
  - serious failures in how the agent worked this session, judged by the criterion in Step 2
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

- Local branches whose content the default branch already holds, and the worktrees attached to them, removed by `git home` and then `git cleanup`, run from the root worktree of each repository this session worked in
  - `git cleanup` judges each branch against the local default branch without fetching, so `git home` pulls first; otherwise a branch merged on GitHub since the last pull survives, and the default branch is checked out at its pre-merge commit
  - Skip both while the working tree has uncommitted changes, since the switch in `git home` would carry them onto the default branch, and report the skip as a line rather than as a failed cleanup
  - When `git home` fails (no remote, offline, a diverged default branch), run `git cleanup` anyway and report the failed pull, since branches the local default branch already holds are still safe to remove
  - `git cleanup` decides each branch on its own content, deletes none while the working tree has uncommitted changes, and leaves a worktree it cannot remove without `--force`, so the run needs no per-branch gate from this skill
  - `git home` switches to the default branch, which fails inside a linked worktree and, in the root worktree, moves the session off the branch it was on, so the report names the switch alongside the branches removed
- A background shell, Monitor, subagent, session cron, or artifact watch this session started whose result the session has already reported
- An open issue from Step 1, closed with `gh issue close` once every item it lists as closing it (the body's request when it lists none) is settled by a merged change or a check run in this session, or once the user said it is not needed or a duplicate
  - Settled items: `--reason completed`, with a comment of a few lines naming what settled each item and linking the PR
  - Not needed: `--reason "not planned"`, and a duplicate of `<M>`: `--duplicate-of <M>`, each with a comment quoting what the user said
  - An issue with an unsettled item stays open, and the report names that item
  - This is the one GitHub write in this class, and it belongs here because reopening the issue undoes it and the comment keeps its basis on record

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
    - The issue is shown with its draft as that proposal's alternative, the pair numbered as one-of-two (3a fix, 3b issue, with "run all" taking the fix), so a declined fix can still leave the defect recorded
    - An issue carries the defect on its own when the session cannot fix it that way
- Findings from scratchpad content are written into the issue or PR itself
  - A file path is not a record, because nobody looks in a place they do not remember

A serious failure in how the agent worked is described to the user and
left without a drafted fix, since the direction a fix takes is theirs to
settle in conversation before any edit is written.

A failure is serious when all three of the following hold. A failure
that misses one costs the user a read and a decision at the end of the
session without changing what they would do: they catch it on the spot
next time, or no edit can keep it from recurring.

- Harm: had it shipped, it would have done one of the following, judged by that impact even when a checkpoint (plan review, PR review, a hook) caught it first
  - changed the direction of the work through a misjudgment
  - left the user to redo work by hand
  - introduced an error into a deliverable
  - misled the user with a confidently wrong assertion
- Cause: a specific instruction text or a missing gate accounts for it, so an edit to a rule, skill, hook, or permission can keep the next session from repeating it
- Exposure: its next occurrence would go unnoticed by the user, or would cause harm that cannot be undone or that leaves the machine

Two adjustments apply to those conditions.

- A failure the agent corrected on its own, before the user pointed it out, stays out even when it repeated within the session
- A failure matching an issue with the `retrospective` label in `ikuwow/dotfiles` is serious when two of the three conditions hold, since its recurrence across sessions shows that leaving it alone did not settle it
  - Find matches with `gh issue list --repo ikuwow/dotfiles --label retrospective --state all --limit 200 --json number,title,state`, reading the body of a candidate whose title alone does not settle the match
  - A closed issue counts, since a recurrence after its fix landed shows the fix did not hold

Each serious failure is presented as follows.

- A session with none says nothing about failures
- Describe each one in a few lines: what happened, how it meets each condition, the risk it carries, the directions a fix could take, and the matching issue when one exists
- A direction is a structural change: an edit to a named instruction text, a new gate (hook, permission, check), or a removal
  - "Be more careful", "follow the rule more closely", recording it in memory, and restating an existing rule are not directions, since each depends on the model's attention or recall improving
- Its one proposal is an issue whose body is that description, so that a session ended before the conversation still keeps the failure on record
  - When the matching issue is open, the proposal is a comment on that issue carrying the description instead
- The issue goes to the session's repository without a label when every direction lands in that project's own rule file, and to `ikuwow/dotfiles` with the `retrospective` label otherwise
- Text for `ikuwow/dotfiles`, a public repository, describes the failure by its behavior pattern and leaves out private repository names, their PR and issue numbers, their code, and quoted text from their rule files

Draft issue and PR titles and bodies against the `pr-issue-writing`
skill, and comments, commit message bodies, and other prose longer than
a sentence with the `technical-writing` skill. This step takes their
writing criteria, and from `pr-issue-writing` also its review of a
draft against its sources, plus its preflight for a proposal that
creates an issue or PR, since Step 4 runs the draft as shown: the
commands that create or edit an issue or PR run in Step 4, for a
selected proposal. A question the preflight would stop to ask becomes
a choice within that proposal in Step 3.

Local git proposals keep to what the session changed.

- A commit proposal names the exact paths it stages, and stages them by path rather than with `git add -A` or `git commit -a`, so another session's changes stay out of it
- Uncommitted changes on the default branch get a proposal to create a branch and commit there

## Step 3: Select

When there are no proposals, go to Step 5, where the cleanup Step 2 already ran is reported.

1. Show every proposal in the conversation, numbered, with its draft in full
   - A serious failure's description comes directly before its proposal, which shows the issue title or the target issue and points to the description as its text, so the user reads the text once
1. Ask for the selection at the end of that same message, in plain text that names the proposal numbers (run 1, run 2, run all, run none), and end the turn there
   - Text sent in the same turn as an AskUserQuestion call can fail to reach the user, so the selection is taken from the user's reply instead
1. Run exactly the proposals the reply selects, and treat every other proposal as declined
   - When the reply neither clearly selects nor clearly declines (an "ok", or a question), ask again rather than guess
   - When the reply changes a draft or asks for another operation, show the revised proposals and ask again before Step 4
   - When the reply takes up the direction of a fix for a serious failure, answer it as conversation, and ask for the selection again once that conversation settles, since the proposals stay open until then

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
