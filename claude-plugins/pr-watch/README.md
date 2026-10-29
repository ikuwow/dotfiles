# pr-watch

pr-watch reports events on GitHub pull requests to the Claude Code session that registered them, one notification line per change, for as long as the session runs. This page is the contract for callers such as skills and agents: the commands, the line format they can match on, and what the watch leaves unreported. The scripts under `bin/` implement it, and a caller depends on this page instead of on them.

The plugin's monitor starts `bin/pr-watch-monitor` with the session, and that watcher runs one `bin/pr-monitor` per registered PR, waiting 60 seconds between polls. The `pr-watch:watch` skill tells an agent how to act on the lines.

## Commands

The plugin puts `bin/` on the PATH of the Bash tool, so an agent runs these by name:

- `pr-watch add <pr>` watches a PR
  - `<pr>` is `<owner>/<repo>#<number>`, `<host>/<owner>/<repo>#<number>`, or a bare number in `GH_REPO` when set, otherwise in the current repository
  - It looks the PR up with `gh`, so it fails for a number that is no PR, and it lists the PR as `<owner>/<repo>#<number>` in the letter case GitHub returns
  - It fails when no watcher runs for the session, so a successful add means the watcher will poll the PR
- `pr-watch remove <owner>/<repo>#<number>` stops a watch, with the PR written as `pr-watch list` prints it
- `pr-watch list` prints the registered PRs whose watch has not ended, and exits 1 whenever no watcher runs

A plugin's own `settings.json` takes only the `agent` and `subagentStatusLine` keys ([Default settings](https://code.claude.com/docs/en/plugins/components.md#default-settings)), so the plugin cannot allow its own commands. A user who wants them to run without a prompt adds these rules to their settings:

```json
"Bash(pr-watch add *)",
"Bash(pr-watch remove *)",
"Bash(pr-watch list)"
```

## Line format

Every line the watcher prints for a PR starts with `<owner>/<repo>#<number> `. An event line follows the prefix with `<EVENT>` or `<EVENT>: <details>`, and any other line with the prefix is `pr-monitor`'s error output. The event names, the `[BOT|USER]` tag, `WATCHING`, and both forms of `WATCH_ERROR` are the stable parts a caller matches on. Detail values are GitHub's own field values, passed through without classification.

The events a PR's line can carry:

| Event | Printed when |
| --- | --- |
| `WATCHING` | Every source has had its first successful poll; every change after this line reports |
| `STATE: <state>` | The PR's state changes, such as `MERGED` or `CLOSED` |
| `REVIEW: <reviewDecision>` | The review decision changes to a non-empty value |
| `READY_FOR_REVIEW` | The PR leaves draft |
| `NEW_COMMENT: [BOT\|USER] <author> <path>:<line>` | A comment arrives in an unresolved, current review thread; `<path>` or `<line>` is `?` where GitHub gives none, as for a file-level comment |
| `NEW_TOP_COMMENT: [BOT\|USER] <author>` | A comment arrives on the PR's conversation |
| `NEW_REVIEW: [BOT\|USER] <author> <state>` | A review with a non-empty body is submitted |
| `CHECK: <name> (<conclusion or state>) @<sha>` | A check on the head commit takes a value other than success, neutral, skipped, and the pending, queued, and running states; `<sha>` is the head commit's first 7 characters |
| `POLL_ERROR: <call>` | A source fails for the first time in a run of failures; `<call>` is `gh pr view`, `gh pr view (rollup)` for a check list that is not an array, `gh api graphql (threads)`, or `gh api graphql (reviews)` |
| `WATCH_ERROR: pr-monitor exited with status <n>` | That PR's watch stopped on an error; the lines just before it with the same prefix carry its error output |

The `[BOT|USER]` tag is `[BOT]` when GitHub's GraphQL `author.__typename` is `Bot`, and `[USER]` otherwise. Comment and review events carry every author, the account `gh` authenticates as included.

Before `WATCHING`, each source takes what its first successful poll finds as already seen, so comments, reviews, and state changes from before the watch began print no line. `CHECK` lines and a `STATE: MERGED` or `STATE: CLOSED` print from the first poll. A PR already merged or closed prints its `STATE:` line and no `WATCHING`. A PR's watch ends at the end of the poll that printed `STATE: MERGED` or `STATE: CLOSED`, so lines from that same poll can follow it.

While `gh pr view` fails, the rest of each poll is skipped, so a `POLL_ERROR: gh pr view` holds back every event of that PR until the call recovers.

A line `WATCH_ERROR: pr-watch-monitor exited with status <n>` without the PR prefix means the watcher itself stopped, and no PR is watched until a new watcher starts with the next session start.

## What the watch does not report

- A check that turns green, so the watch cannot end a wait on CI
- A comment in a review thread while the thread is resolved or outdated; once the thread is unresolved, its comments not yet reported print, those from before the watch began included
- A PR turned back into a draft
- The recovery from a `POLL_ERROR`, and the cause of the failure
- A review thread, comment, or review past the first 100 of its kind, since `pr-monitor` reads each with `first:100`

## Limits

Session ID:

- The watch list is keyed by `CLAUDE_CODE_SESSION_ID`, and `/clear` gives Bash a new one, so if the running watcher keeps the old ID, an add after a `/clear` fails; whether it keeps the old ID or a second watcher starts is unmeasured
- `claude --resume <session-id>` keeps the session ID, and the watches resume; `--continue` and an in-session `/resume` are unmeasured
- Two Claude processes with one session ID, or a reload that starts a watcher while the old one is exiting, can leave no watcher running with no line printed

Coverage:

- A comment the session itself posts comes back as an event and wakes the session

Concurrency:

- A `remove` rewrites the list, so an `add` landing between its read and its write is lost; run `add` and `remove` one at a time

Lifecycle and install:

- State lives under `${XDG_STATE_HOME:-~/.local/state}/pr-watch/`, three files per session ID; a running watcher touches its own every loop, and each watcher start deletes the files untouched for 30 days, so a session resumed more than 30 days after its watcher stopped starts with no watches
- A SIGKILL of the watcher prints no `WATCH_ERROR`, and a `pr-monitor` killed with SIGKILL leaves its three temporary files in `$TMPDIR`; a SIGTERM removes them
- A change to `monitors.json` or to `bin/pr-watch-monitor` reaches a session at its next start; `/reload-plugins` did not start the watcher again in a session where the monitor's command had changed
  - A session whose watcher predates the session-ID argument on the watcher's command line fails every `add` and `list` until it restarts, since `pr-watch` matches that argument
- An add lists the PR without its host, so `pr-monitor` polls it on `gh`'s default host
- The marketplace path in the dotfiles `claude/settings.json` is absolute; whether `~` works there, and what `claude plugin marketplace add` does on a machine with another `$HOME` where that name is already declared, are unverified
