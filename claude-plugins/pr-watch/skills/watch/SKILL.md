---
name: watch
description: Watch a GitHub pull request for new comments, reviews, failing checks, a ready-for-review flip, and merge or close, with each change delivered to this Claude Code session as a notification for as long as the session runs, idle or not. Use whenever a workflow says to watch, monitor, or wait on a PR's review activity or state, to stop watching a PR, or when a notification line starting with `<owner>/<repo>#<number>` or `WATCH_ERROR` arrives.
---

# Watch a PR

The pr-watch plugin's monitor runs `pr-watch-monitor` for the whole session. It polls each registered PR every 60s and prints one line per actionable change, and each line reaches the session as a notification, so a watch runs across turns without a restart.

## Start and stop a watch

- `pr-watch add <pr>` watches a PR, where `<pr>` is `<owner>/<repo>#<number>` or a bare number in `GH_REPO` when set, otherwise in the current repository
  - A failing add means the PR is not watched: report the error it printed, and claim no ongoing wait on that PR
- `pr-watch remove <owner>/<repo>#<number>` stops a watch, with the PR written as `pr-watch list` prints it
- `pr-watch list` prints the registered PRs not recorded as finished, and exits 1 whenever no watcher runs

Run `add` and `remove` one at a time rather than in parallel tool calls, since a `remove` rewrites the list and can drop an `add` that lands at the same moment.

## Read the lines

- An event line is `<owner>/<repo>#<number> <EVENT>` or `<owner>/<repo>#<number> <EVENT>: <details>`, carrying GitHub's own field values; the header of `${CLAUDE_PLUGIN_ROOT}/bin/pr-monitor` documents every event
- `<owner>/<repo>#<number> WATCHING` means every change from now on reports: re-fetch the PR when it arrives
  - Before it, comments, reviews, and state changes the watch found on its first polls were taken as already seen, so the re-fetch on it covers the time before the watch began
  - It follows a start of a watch, whether by an add, a restart after `WATCH_ERROR`, or a resumed session, unless the PR is already merged or closed, which prints `STATE:` instead, or its first `gh pr view` keeps failing, which prints `POLL_ERROR`
- `CHECK` lines end with `@<sha>`, the head commit the check ran on, so a failure reported again after a restart shows the same sha as before
- A check that turns green prints no line, so the watch cannot end a wait on CI; `gh pr checks --watch --fail-fast` with `run_in_background: true` covers that
- Comments in a resolved or outdated review thread print no line, so a reply in a thread a push has made outdated has to be found by a re-fetch
- `POLL_ERROR: <call>` prints when that call first fails, and neither its later failures nor its recovery print a line
  - Events from that call are delayed until it recovers, and a failing `gh pr view` holds back the whole watch
  - Re-fetch the PR to see where it stands
- A PR's watch ends on its own after its `STATE: MERGED` or `STATE: CLOSED` line

## When a watch stops

- `<owner>/<repo>#<number> WATCH_ERROR` means that PR's watch stopped
  - Report it together with the lines just before it with the same prefix, which carry `pr-monitor`'s error output
  - Restart it with `pr-watch add <owner>/<repo>#<number>`, then re-fetch on its `WATCHING` line
- `WATCH_ERROR` with no `<owner>/<repo>#<number>` means the watcher itself stopped, and no PR is watched until a new watcher starts: report it, and claim no ongoing wait on any PR
  - A session restart starts one, and its watches each print `WATCHING` again
- When the session ends, its watches stop; resuming the same session starts every unfinished watch again, each with a `WATCHING` line, and a PR that merged or closed in between prints its `STATE:` line instead
  - That holds when the resumed session keeps its session ID, which `claude --resume <session-id>` does; after any resume, run `pr-watch list`, and when it exits 1, report that no PR is watched and claim no ongoing wait
