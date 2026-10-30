---
name: watch
description: Watch a GitHub pull request for new comments, reviews, review requests added or removed, dismissed reviews, failing checks, a flip into or out of draft, and merge or close, with each change delivered to this Claude Code session as a notification for as long as the session runs, idle or not. Use whenever a workflow says to watch, monitor, or wait on a PR's review activity or state, to stop watching a PR, or when a notification line starting with `<owner>/<repo>#<number>` or `WATCH_ERROR` arrives.
---

# Watch a PR

The pr-watch plugin's monitor runs `pr-watch-monitor` for the whole session. It polls each registered PR every 60s and prints one line per actionable change, and each line reaches the session as a notification, so a watch runs across turns without a restart.

## Start and stop a watch

- `pr-watch add <pr>` watches a PR, where `<pr>` is `<owner>/<repo>#<number>` or a bare number in `GH_REPO` when set, otherwise in the current repository
  - Watch only PRs on github.com, since the list keeps no host and the watch polls github.com
  - It looks the PR up with `gh` and lists it as `<owner>/<repo>#<number>` in the letter case GitHub returns, so a number that is no PR fails
  - A failing add means the PR is not watched: report the error it printed, and claim no ongoing wait on that PR
  - An add of a PR whose watch is running keeps that watch, and prints no new `WATCHING`
- `pr-watch remove <owner>/<repo>#<number>` stops a watch, with the PR written as `pr-watch list` prints it
- `pr-watch list` prints the registered PRs whose watch has not ended, and exits 1 whenever no watcher runs

Run `add` and `remove` one at a time rather than in parallel tool calls, since a `remove` rewrites the list and can drop an `add` that lands at the same moment.

## Read the lines

Every line for a PR starts with `<owner>/<repo>#<number> `. An event line follows it with `<EVENT>` or `<EVENT>: <details>`, where the details are GitHub's own field values, passed through without classification. Any other line with the prefix is `pr-monitor`'s error output.

A re-fetch below reads the PR's state, comments, reviews, review threads, requested reviewers, and checks again with `gh`, through the commands the calling workflow names when it names them.

| Event | Printed when |
| --- | --- |
| `WATCHING` | Every source has had its first successful poll; every change after this line reports |
| `STATE: <state>` | The PR is merged, closed, or reopened, as `MERGED`, `CLOSED`, or `OPEN`; a merge can print `STATE: MERGED` and then `STATE: CLOSED`, since GitHub records both |
| `REVIEW: <reviewDecision>` | The review decision changes to a non-empty value |
| `READY_FOR_REVIEW` | The PR leaves draft |
| `CONVERT_TO_DRAFT` | The PR goes back to draft |
| `REVIEW_DISMISSED` | A review is dismissed; the re-fetch's reviews show which one |
| `NEW_COMMENT: [BOT\|USER] <author> <path>:<line>` | A comment arrives in an unresolved, current review thread; `<path>` or `<line>` is `?` where GitHub gives none, as for a file-level comment |
| `NEW_TOP_COMMENT: [BOT\|USER] <author>` | A comment arrives on the PR's conversation |
| `NEW_REVIEW: [BOT\|USER] <author> <state>` | A review with a non-empty body is submitted |
| `REVIEW_REQUESTED: [<TYPE>] <reviewer> by <actor>` | `<actor>` requests a review from `<reviewer>`, including a re-request after that reviewer's review |
| `REVIEW_REQUEST_REMOVED: [<TYPE>] <reviewer> by <actor>` | `<actor>` removes `<reviewer>` from the requested reviewers; a reviewer leaving the list by submitting a review prints no line |
| `CHECK: <name> (<conclusion or state>) @<sha>` | A check on the head commit takes a value other than success, neutral, skipped, and the pending, queued, and running states; `<sha>` is the head commit's first 7 characters |
| `POLL_ERROR: <source>` | A source fails for the first time in a run of failures; `<source>` is `graphql (pull request)`, `graphql (checks)` for a check list of no known shape, `graphql (threads)`, or `graphql (timeline)` |
| `WATCH_ERROR: pr-monitor exited with status <n>` | That PR's watch stopped on an error |

- `[BOT]` marks an author whose GraphQL `author.__typename` is `Bot`, and `[USER]` every other author, with `<author>` as `?` where GitHub gives none, as for a deleted account
  - Comment and review events carry every author, the account `gh` authenticates as included, so check on the re-fetch whether a comment or review is a post this session made before acting on it
- `[<TYPE>]` on a review-request line is the reviewer's GraphQL `__typename` in upper case, such as `[USER]`, `[TEAM]`, `[BOT]`, or `[MANNEQUIN]`, and a team's `<reviewer>` is `<org>/<team>`
  - `[<TYPE>]`, `<reviewer>`, or `<actor>` is `?` where GitHub gives none, as for a deleted account
  - The last review-request line for a reviewer is where that reviewer stands; the re-fetch's requested reviewers are the current list
  - A team whose code review auto assignment removes the team's request can print the team's `REVIEW_REQUESTED` and `REVIEW_REQUEST_REMOVED` with a `REVIEW_REQUESTED` for each member assigned
- On `WATCHING`, re-fetch the PR
  - Before it, each source took what its first successful poll found as already seen, so comments, reviews, review requests, and state changes from before the watch began printed no line, and the re-fetch covers them
  - It follows each new start of a watch, by an add, a restart after `WATCH_ERROR`, or a resumed session, unless the PR is already merged or closed, which prints its `STATE:` line instead, or a source's first poll keeps failing, which prints that source's `POLL_ERROR`
- `NEW_TOP_COMMENT`, `NEW_REVIEW`, the review-request lines, `READY_FOR_REVIEW`, `CONVERT_TO_DRAFT`, `REVIEW_DISMISSED`, and `STATE` come from the PR's timeline, one line per reported timeline item in the timeline's order
  - Each line marks that the item exists, so re-fetch the PR for its content
- `CHECK` lines and a `STATE: MERGED` or `STATE: CLOSED` line print from the first poll
  - Treat a `CHECK` line whose name and `@<sha>` match one already handled as a repeat, as after a restart
  - Each check reports on its own, so checks sharing a name can print lines that read alike, and `gh pr view --json statusCheckRollup` lists each of them
- A PR's watch ends on its own with the first poll that finds the PR merged or closed, printing its `STATE: MERGED` or `STATE: CLOSED` line in that poll unless the timeline has already printed it, so lines from that poll can follow it
  - A poll whose last `STATE` line is `STATE: OPEN` finds the PR reopened, and the watch goes on
- `POLL_ERROR` prints only when a source first fails; neither its later failures, its recovery, nor its cause print a line
  - Events from that source wait until it recovers; a timeline item prints even when what it changed has reverted by then, while a check or review decision that reverts, or a review-thread comment whose thread is resolved or outdated by then, prints no line, and a failing `graphql (pull request)` holds back every event of the PR
  - Re-fetch the PR to see where it stands

## What the watch does not report

Re-fetch the PR to find these, since no line reports them:

- A check that turns green, so the watch cannot end a wait on CI; `gh pr checks --watch --fail-fast` with `run_in_background: true` covers that
- A comment in a review thread while the thread is resolved or outdated, such as a reply in a thread a push has made outdated
  - Once the thread is unresolved and current, its comments not yet reported print, those from before the watch began included
- A review thread, or a comment in one, past the first 100 of its kind
- A check past the first 100 on the head commit
- A timeline item pushed out of the newest 100 before a poll reads it, as when more than 100 arrive during a `POLL_ERROR` outage

## When a watch stops

- `<owner>/<repo>#<number> WATCH_ERROR` means that PR's watch stopped
  - Report it together with the lines just before it with the same prefix, which carry `pr-monitor`'s error output
  - Restart it once with `pr-watch add <owner>/<repo>#<number>`, then re-fetch on its `WATCHING` line; on a second `WATCH_ERROR` for the PR, report it and claim no ongoing wait on that PR
- `WATCH_ERROR: pr-watch-monitor exited with status <n>` with no `<owner>/<repo>#<number>` means the watcher itself stopped, and no PR is watched until a new watcher starts: report it, and claim no ongoing wait on any PR
- When the session ends, its watches stop; resuming the session under the same session ID (`claude --resume <session-id>`) starts a new watcher, which starts every unfinished watch again, each with a `WATCHING` line, and a PR that merged or closed in between prints its `STATE:` line instead
- A watcher can also stop without a line, so before saying in a later turn that a PR is still watched, run `pr-watch list`; when it exits 1 or omits the PR, report that the PR is not watched and claim no ongoing wait on it
