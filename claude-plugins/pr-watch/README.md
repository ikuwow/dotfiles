# pr-watch

pr-watch reports events on GitHub pull requests to the Claude Code session that registered them, one notification line per change, for as long as the session runs. This page is the contract for callers such as skills and agents: the commands, the line format they can match on, and what the watch leaves unreported. The scripts under `bin/` implement it, and a caller depends on this page instead of on them.

The plugin's monitor starts `bin/pr-watch-monitor` with the session, and that watcher runs one `bin/pr-monitor` per registered PR, polling it every 60 seconds. The `pr-watch:watch` skill tells an agent how to act on the lines.

## Commands

The plugin puts `bin/` on the PATH of the Bash tool, so an agent runs these by name:

- `pr-watch add <pr>` watches a PR
  - `<pr>` is `<owner>/<repo>#<number>`, `<host>/<owner>/<repo>#<number>`, or a bare number in `GH_REPO` when set, otherwise in the current repository
  - It looks the PR up with `gh`, so it fails for a number that is no PR, and it lists the PR as `<owner>/<repo>#<number>` in the letter case GitHub returns
  - It fails when no watcher runs for the session, so a successful add means events will arrive
- `pr-watch remove <owner>/<repo>#<number>` stops a watch, with the PR written as `pr-watch list` prints it
- `pr-watch list` prints the registered PRs whose watch has not ended, and exits 1 whenever no watcher runs

A plugin's own `settings.json` takes only the `agent` and `subagentStatusLine` keys ([Default settings](https://code.claude.com/docs/en/plugins/components.md#default-settings)), so the plugin cannot allow its own commands. A user who wants them to run without a prompt adds these rules to their settings:

```json
"Bash(pr-watch add *)",
"Bash(pr-watch remove *)",
"Bash(pr-watch list)"
```

## Line format

Every line the watcher prints for a PR starts with `<owner>/<repo>#<number> `, followed by `<EVENT>` or `<EVENT>: <details>`. The event names, the `[BOT|USER]` tag, `WATCHING`, and both forms of `WATCH_ERROR` are the stable parts a caller matches on. Detail values are GitHub's own field values, passed through without classification.

The events a PR's line can carry:

| Event | Printed when |
| --- | --- |
| `WATCHING` | Every source has had its first successful poll; every change after this line reports |
| `STATE: <state>` | The PR's state changes, such as `MERGED` or `CLOSED` |
| `REVIEW: <reviewDecision>` | The review decision changes to a non-empty value |
| `READY_FOR_REVIEW` | The PR leaves draft |
| `NEW_COMMENT: [BOT\|USER] <author> <path>:<line>` | A comment arrives in an unresolved, current review thread |
| `NEW_TOP_COMMENT: [BOT\|USER] <author>` | A comment arrives on the PR's conversation |
| `NEW_REVIEW: [BOT\|USER] <author> <state>` | A review with a non-empty body is submitted |
| `CHECK: <name> (<conclusion or state>) @<sha>` | A check on the head commit settles on anything but success, neutral, or skipped; `<sha>` is the head commit's first 7 characters |
| `POLL_ERROR: <call>` | A call to GitHub fails for the first time in a run of failures |
| `WATCH_ERROR: pr-monitor exited with status <n>` | That PR's watch stopped on an error; the lines just before it with the same prefix carry its error output |

The `[BOT|USER]` tag is `[BOT]` when GitHub's GraphQL `author.__typename` is `Bot`, and `[USER]` otherwise. Comment and review events carry every author, the account `gh` authenticates as included.

Before `WATCHING`, each source takes what its first successful poll finds as already seen, so comments, reviews, and state changes from before the watch began print no line. `CHECK` lines and a `STATE: MERGED` or `STATE: CLOSED` print from the first poll. A PR already merged or closed prints its `STATE:` line and no `WATCHING`, and a PR's watch ends after its `STATE: MERGED` or `STATE: CLOSED` line.

A line `WATCH_ERROR: pr-watch-monitor exited with status <n>` without the PR prefix means the watcher itself stopped, and no PR is watched until a new watcher starts with the next session start.

## What the watch does not report

- A check that turns green, so the watch cannot end a wait on CI
- A comment in a resolved or outdated review thread
- A PR turned back into a draft
- The recovery from a `POLL_ERROR`, and the cause of the failure
- A review thread, comment, or review past the first 100 of its kind, since `pr-monitor` reads each with `first:100`

## Limits

Session ID:

- The watch list is keyed by `CLAUDE_CODE_SESSION_ID`, and `/clear` gives Bash a new one, so an add after a `/clear` fails; whether the running watcher keeps the old ID or a second watcher starts is unmeasured
- `claude --resume <session-id>` keeps the session ID, and the watches resume; `--continue` and an in-session `/resume` are unmeasured
- Two Claude processes with one session ID, or a reload that starts a watcher while the old one is exiting, can leave no watcher running with no line printed

Coverage:

- A comment the session itself posts comes back as an event and wakes the session

Concurrency:

- A `remove` rewrites the list, so an `add` landing between its read and its write is lost; run `add` and `remove` one at a time

Lifecycle and install:

- State lives under `${XDG_STATE_HOME:-~/.local/state}/pr-watch/`, three files per session ID, and each watcher start deletes the files no add, remove, or finished watch has written to for 30 days; a session resumed after that starts with no watches
- A SIGKILL of the watcher prints no `WATCH_ERROR`, and a `pr-monitor` killed with SIGKILL leaves its three temporary files in `$TMPDIR`; a SIGTERM removes them
- A change to `monitors.json` or to `bin/pr-watch-monitor` reaches a session at its next start; `/reload-plugins` did not start the watcher again in a session where the monitor's command had changed
- An add lists the PR without its host, so `pr-monitor` polls it on `gh`'s default host
- The marketplace path in the dotfiles `claude/settings.json` is absolute; whether `~` works there, and what `claude plugin marketplace add` does on a machine with another `$HOME` where that name is already declared, are unverified
