---
name: wrap-up
description: End a session quickly and safely. Finish without asking whatever is quick and can be undone (routine cleanup, issue checkboxes, PR body fixes, small promised work, records on the user's own issues and PRs), ask once about everything else in a single list, and report whether the session is safe to end, along with any serious failure in how the agent worked. Trigger when the user signals that the session or the task is over ("終わり", "done", "これで完了", "おつかれ"), when they ask what is left before quitting, and when they invoke /wrap-up.
---

# Wrap Up

The user invokes this skill to leave the session, so what it costs them
is the turns it takes and the text it makes them read. One test sorts
every item that needs action: is it quick, and can it be undone? An item
that passes runs without a question and appears in the report. An item
that fails goes on one list, which the user answers once, and so do
three kinds of write whose cost an undo does not return.

When the user only asks what is left, answer from Step 1's inventory and
stop there, since a question does not say the work is over. Steps 2 to 4
run once the user says the session or the task is over.

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
  - `gh pr view <number> --repo <owner>/<repo> --json state,isDraft,statusCheckRollup,reviewDecision,author,body`
  - unresolved review threads, listed by `gh pr-review review view -R <owner>/<repo> <number> --unresolved --not_outdated`
- Open issues that those PRs address or that the user named as the work target, read with `gh issue view <number> --repo <owner>/<repo> --json title,body,state,comments,author,assignees`
- Work that runs only while this session is open
  - background shells, Monitors, and subagents this session started, identified from its own `run_in_background`, Monitor, and Agent calls
  - PR watches, listed by `pr-watch list` (the `pr-watch:watch` skill)
  - session crons, listed by `CronList`
  - artifact watches, listed by the `ArtifactComments` tool's `watch` action with no `url`
- The conversation and scratchpad content
  - work the session said it would do and did not finish
  - questions put to the user that have no answer yet
  - findings that pass the record test in Step 2
  - serious failures in how the agent worked, by the test in Step 4's report

Attribute each uncommitted change and stash entry before acting on it,
and act only on those this session made. Another concurrent session may
share the working tree and the stash, and committing its edits would
ship them under this session's intent.

An item already safe to leave (pushed, recorded in an issue or PR, or
finished) needs no action and no mention.

## Step 2: Do what is quick and can be undone

Run each item below as it is found, without naming it to the user
first. Asking about one costs the user a decision to protect state they
can restore.

- Quick: it finishes in this turn within a few minutes, with no new PR and no wait on CI, a review, or another outside result
- Can be undone: it removes local state whose content exists somewhere the user can still reach, or it writes to something the user owns in a way git or GitHub reverses (a comment is edited or deleted, a body keeps its edit history, an issue reopens, a commit is followed by another)
- The user owns a PR they authored, and an issue whose `assignees` include their login (`gh api user --jq .login`) or that they authored with `assignees` empty

An item that fits Step 3's `new`, `others`, or `wider` tag goes on the
list even when it passes both.

The items:

- Local branches whose content the default branch already holds, and the worktrees attached to them, removed by `git home` and then `git cleanup`, run from the root worktree of each repository this session worked in
  - It runs here whichever session created a branch or worktree, since what it removes holds no content that a remaining ref lacks
  - `git cleanup` judges each branch against the local default branch without fetching, so `git home` pulls first
  - Skip both while the working tree has uncommitted changes, since the switch in `git home` would carry them onto the default branch, and report the skip
  - When `git home` fails (no remote, offline, a diverged default branch), run `git cleanup` anyway and report the failed pull
  - `git home` moves the session onto the default branch, so the report names the switch alongside the branches removed
- A background shell, Monitor, subagent, session cron, or artifact watch this session started whose result the session has already reported
- A PR watch on a PR whose outcome the session has already reported, stopped through the `pr-watch:watch` skill, since a resumed session would otherwise start it again
- Checkboxes in the user's issues and PRs, ticked for each item that a merged change or a check run in this session settled
- A statement in the body of the user's PR that this session's work made untrue, corrected
- An open issue the user owns, closed with `gh issue close` once every item it lists as closing it (the body's request when it lists none) is settled, or once the user said it is not needed or a duplicate
  - Settled: `--reason completed`, with a comment of a few lines naming what settled each item and linking the PR
  - Not needed: `--reason "not planned"`, and a duplicate of `<M>`: `--duplicate-of <M>`, each with a comment quoting what the user said
- Work the session said it would do and did not finish, when it lies within what the user asked for and passes the quick test
- This session's finished changes left uncommitted on its feature branch, committed and pushed
  - Stage by path, never with `git add -A` or `git commit -a`, so another session's changes stay out
  - When the push starts CI, report that it is running rather than waiting for it
- A finding that passes the record test, written as a comment on the issue or PR of the user's that tracks the work

The record test: a finding is recorded only when it changes what a
reader of that issue or PR decides or does next. A finding that restates
documented tool behavior, or what the target already says, fails it.
So does a problem that only a vendor or the OS can fix, since no
repository's owner can act on it. Write the finding itself into the
comment, since nobody looks for a scratchpad path they do not remember.

Issue and PR bodies and comments written in this step go through the
`pr-issue-writing` skill, and commit message bodies through
`technical-writing`. A write that `pr-issue-writing` would stop to ask
about goes on Step 3's list instead.

## Step 3: Ask once about the rest

Everything else that needs action goes on the list, tagged with the
reason it is there.

- `slow`: work that fails the quick test, such as a fix that needs a new PR, unfinished work that takes longer than a few minutes, or uncommitted changes on the default branch, which need a branch and a PR of their own
- `permanent`: a removal of content held nowhere else (uncommitted changes, a stash entry, an unpushed commit)
- `new`: creating an issue or a PR, since the user has to triage what it adds
- `others`: a write to an issue or PR the user does not own, a push to a branch other than this session's feature branch, and an operation on state another session created
  - The object written to decides this, so the user's own PR and this session's branch in an organization's repository are the user's
- `wider`: a write to a repository visible to more people than one the session worked in (private to internal or public, internal to public), since its readers have the text from the moment it is posted

With nothing on the list, go to Step 4.

1. Show the list numbered, one line per item: the operation, its target, and its tag
   - Show no draft text, since text is written only for what the user selects
   - A `wider` item is the exception: its line names the target repository and its visibility, and its full draft follows, written through `pr-issue-writing`, so the user reads the text before the target's readers do
     - When that skill stops on a question, the question takes the draft's place, and the item cannot be selected in this wrap-up, since its text was never shown
1. Ask which to run at the end of that same message, in plain text, and end the turn there
   - Text sent in the same turn as an AskUserQuestion call can fail to reach the user
1. Act on the reply without asking again
   - Numbers select those items
   - A go-ahead without numbers ("ok", "はよ", "go") selects every item except those tagged `slow`, `permanent`, or `wider`, since it asks for the session to end sooner and names no removal and no wider post; on a one-item list it selects that item unless the item is tagged `wider`
   - A reply that changes an item, or names another operation and its target, is run as the reply states it, except where Step 4 holds a `wider` write back
   - An item the reply leaves undecided does not run

## Step 4: Run and report

Write the text for each selected item, then run it. A `wider` write
is posted only as its draft was shown. One whose draft was not shown, or
whose text the reply changes, is not posted, and the report carries its
draft, or the question that stopped it. Issue and PR
titles, bodies, and comments go through the `pr-issue-writing` skill,
and commit message bodies through `technical-writing`. A question
`pr-issue-writing` would stop to ask (a duplicate it found, a contact
channel in the template config) stops that item, and the report carries
the question.

Each item ends at the last operation its line names, so a commit stops
at the commit. When an item cannot run as listed (a command fails, or
the target has changed), stop it and every selected item that needs it.

`slow` work that was not selected is recorded in one line as a comment
on the user's issue or PR that tracks it, when one exists and the
comment fits no tag.

The report:

1. Open with the verdict
   - Safe to end: every operation in Step 2 and every selected item ran
   - Items remain: one of them failed or was stopped
1. List what ran, one line per operation, with the URL of anything posted or edited, so the user can find it to undo it
1. For each item that did not run, write one line naming where it now lives: a PR or issue URL, a place that exists only on this machine (uncommitted changes, a stash entry, or an unpushed branch, with its repository), or what ending the session stops or discards
1. Describe each serious failure in how the agent worked in one or two lines: what the agent did and what it cost the user
   - A failure is serious when the user had to correct it or redo work because of it, when it put an error into a deliverable or a wrong assertion in front of the user, or when it spent the user's turns on a stop or a confirmation the task did not need
   - Leave out one the agent corrected on its own before the user pointed it out or this wrap-up began, and say nothing about failures when none is serious
   - Give no cause for it, propose no change to a rule, skill, or hook, and write no record of it, since one session shows one instance: whether to act on it, and where a change belongs (a global rule, a project rule, a skill, or a hook), is settled with the user in the conversation that follows
   - A defect the failure left in a deliverable is still an item in Step 2 or Step 3
