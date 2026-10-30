# pr-watch

pr-watch reports events on GitHub pull requests to the Claude Code session that registered them, one notification line per change, for as long as the session runs. The `pr-watch:watch` skill (`skills/watch/SKILL.md`) is what a calling agent reads: the commands, the line format, the events, and what the watch leaves unreported. This page is for maintaining the plugin.

## Requirements

- A `gh` logged in to github.com, whose token `pr-monitor` reads with `gh auth token`
- Python 3.9 or later for `pr-monitor`, standard library only
- bash 4 or later for `pr-watch` and `pr-watch-monitor`
- A local machine: the GitHub proxy of an Anthropic-hosted cloud session rejects GraphQL ([GitHub proxy](https://code.claude.com/docs/en/cloud-environments.md#github-proxy))

## How it runs

- `monitors/monitors.json` starts `bin/pr-watch-monitor` with each session
  - The watcher re-execs itself with the session ID as its argument, so `pr-watch` tells this session's watcher from another session's by its command line
  - It runs one `bin/pr-monitor` per registered PR, waiting 60 seconds between polls, and prefixes each line with the PR
- `bin/pr-watch` edits the session's list and checks that the session's watcher runs
- State lives under `${XDG_STATE_HOME:-~/.local/state}/pr-watch/`, three files per session ID: the list, `<list>.done`, and `<list>.pid`
  - A running watcher touches its own every loop, and each watcher start deletes the files untouched for 30 days
- `scripts/claude-code-setup.sh` adds `claude-plugins/` as a local marketplace, so the plugin loads in place from this checkout

The lines `pr-monitor` and `pr-watch-monitor` print are the contract `SKILL.md` documents, so a change to an event's name, format, or timing changes `SKILL.md` in the same commit.

## Allow rules

A plugin's own `settings.json` takes only the `agent` and `subagentStatusLine` keys ([Default settings](https://code.claude.com/docs/en/plugins/components.md#default-settings)), so the plugin cannot allow its own commands. A user who wants them to run without a prompt adds these rules to their settings:

```json
"Bash(pr-watch add *)",
"Bash(pr-watch remove *)",
"Bash(pr-watch list)"
```

## Limits

Session ID:

- The watch list is keyed by `CLAUDE_CODE_SESSION_ID`, and `/clear` gives Bash a new one, so if the running watcher keeps the old ID, an add after a `/clear` fails; whether it keeps the old ID or a second watcher starts is unmeasured
- `claude --resume <session-id>` keeps the session ID, and the watches resume; `--continue` and an in-session `/resume` are unmeasured
- Two Claude processes with one session ID, or a reload that starts a watcher while the old one is exiting, can leave no watcher running with no line printed

Concurrency:

- A `remove` rewrites the list, so an `add` landing between its read and its write is lost

Lifecycle and install:

- A session resumed more than 30 days after its watcher stopped starts with no watches, since its state files are gone
- A SIGKILL of the watcher prints no `WATCH_ERROR`
- A change to `monitors.json` or to `bin/pr-watch-monitor` reaches a session at its next start; `/reload-plugins` did not start the watcher again in a session where the monitor's command had changed
- An add lists the PR without its host, and `pr-monitor` polls github.com, so a PR on another host fails with `POLL_ERROR` or reads as a same-named PR on github.com
- The marketplace path in the dotfiles `claude/settings.json` is absolute; whether `~` works there, and what `claude plugin marketplace add` does on a machine with another `$HOME` where that name is already declared, are unverified
