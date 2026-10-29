---
name: watch
description: Watch a GitHub pull request for new comments, reviews, failing checks, a ready-for-review flip, and merge or close, with each change delivered to this Claude Code session as a notification for as long as the session runs, idle or not. Use whenever a workflow says to watch, monitor, or wait on a PR's review activity or state, to stop watching a PR, or when a notification line starting with `<owner>/<repo>#<number>` or `WATCH_ERROR` arrives.
---

# Watch a PR

The pr-watch plugin's monitor runs `pr-watch-monitor` for the whole session. It polls each registered PR every 60s and prints one line per actionable change, and each line reaches the session as a notification, so a watch runs across turns without a restart.

## Start and stop a watch

- `pr-watch add <number>` watches a PR of the current repository; prefix `GH_REPO=<owner>/<repo>` for a PR of another one
  - A failing add means the PR is not watched: report the error it printed, and claim no ongoing wait on that PR
  - Re-fetch the PR right after the add, since the watch's first poll takes what already happened as seen
- `pr-watch remove <number>` stops a watch
- `pr-watch list` prints the registered PRs not recorded as finished, and exits 1 when no watcher runs to watch them

Run `add` and `remove` one at a time rather than in parallel tool calls, since a `remove` rewrites the list and can drop an `add` that lands at the same moment.

## Read the lines

- An event line is `<owner>/<repo>#<number> <EVENT>` or `<owner>/<repo>#<number> <EVENT>: <details>`, carrying GitHub's own field values; the header of `${CLAUDE_PLUGIN_ROOT}/bin/pr-monitor` documents every event
- The first poll runs about 10s after the add and records what already holds without reporting it, except a failing check and a PR already merged or closed, so any change in that window, a ready flip included, does not report
- A check that turns green prints no line, so the watch cannot end a wait on CI; `gh pr checks --watch --fail-fast` with `run_in_background: true` covers that
- Comments in a resolved or outdated review thread print no line, so a reply in a thread a push has made outdated has to be found by a re-fetch
- `POLL_ERROR: <call>` means that call keeps failing, and no line reports its recovery: re-fetch the PR to see where it stands, and treat events as possibly missed until a later event arrives
- A PR's watch ends on its own after its `STATE: MERGED` or `STATE: CLOSED` line

## When a watch stops

- `<owner>/<repo>#<number> WATCH_ERROR` means that PR's watch stopped
  - Report the line together with the lines before it that carry the same prefix, which hold the cause
  - Restart it with `GH_REPO=<owner>/<repo> pr-watch add <number>`, then re-fetch the PR
- `WATCH_ERROR` with no `<owner>/<repo>#<number>` means the watcher itself stopped and no PR is watched until the session restarts: report it, and claim no ongoing wait on any PR
- When the session ends, its watches stop; resuming the same session starts every unfinished watch again, and a PR that merged or closed in between reports its `STATE:` line on that first poll
