---
name: watch
description: Watch a GitHub pull request for new comments, reviews, failing checks, a ready-for-review flip, and merge or close, with each change delivered to this Claude Code session as a notification for as long as the session runs, idle or not. Use whenever a workflow says to watch, monitor, or wait on a PR's review activity or state, to stop watching a PR, or when a notification line starting with `<owner>/<repo>#<number>` or `WATCH_ERROR` arrives.
---

# Watch a PR

The pr-watch plugin's monitor runs `pr-watch-monitor` for the whole session. It polls each registered PR every 60s and prints one line per actionable change, and each line reaches the session as a notification. A watch keeps running across turns until its PR merges or closes, so nothing is re-armed.

## Start and stop a watch

- `pr-watch add <number>` watches a PR of the current repository; prefix `GH_REPO=<owner>/<repo>` for a PR of another one
  - A failing add means the PR is not watched: report the error it printed, and claim no ongoing wait on that PR
- `pr-watch remove <number>` stops a watch
- `pr-watch list` prints the PRs whose watch has not finished

## Read the lines

- An event line is `<owner>/<repo>#<number> <EVENT>` or `<owner>/<repo>#<number> <EVENT>: <details>`, carrying GitHub's own field values
  - The header of `${CLAUDE_PLUGIN_ROOT}/bin/pr-monitor` documents every event, and the event names and the `[BOT|USER]` author tag stay stable, since callers react by them
- The first poll of a watch records what already holds without reporting it, except a failing check and a PR already merged or closed
  - It runs up to 10s after the add, so a PR flipped to ready within that window may never report `READY_FOR_REVIEW`
- A check that turns green prints no line, so the watch cannot end a wait on CI; `gh pr checks --watch --fail-fast` with `run_in_background: true` covers that
- A PR's watch ends on its own after its `STATE: MERGED` or `STATE: CLOSED` line

## When a watch stops

- `<owner>/<repo>#<number> WATCH_ERROR` means that PR's watch stopped
  - Report the line together with the lines before it that carry the same prefix, which hold the cause
  - Restart it with `GH_REPO=<owner>/<repo> pr-watch add <number>`, then re-fetch the PR, since the restarted watch takes what already happened as seen
- `WATCH_ERROR` with no `<owner>/<repo>#<number>` means the watcher itself stopped and no PR is watched until the session restarts: report it, and claim no ongoing wait on any PR
