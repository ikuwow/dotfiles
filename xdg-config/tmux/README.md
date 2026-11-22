# tmux

`tmux.conf` is the tmux configuration, deployed with this directory to
`~/.config/tmux/`. The prefix is `C-q`. After editing, reload it in a
running server with `tmux source-file ~/.config/tmux/tmux.conf`; a
setting removed from the file keeps its old value until the server
restarts.

The terminal's title, which Ghostty shows as the tab name, is the tmux
session's name; `ide` names a session after its project's directory
and titles its sessions `IDE: <name>`, followed by the title of the
Claude Code pane shown in the window.

## Tabs in a pane

A pane can hold several tabs, one shown at a time, such as further
shells or Claude Code sessions in the right pane that `ide` opens. In
the window `ide` opens, every pane's top border lists its tabs, with
the shown tab in reverse video, and a pane without tabs shows itself as
tab 1; a Claude Code tab is labeled with its session title. Another
window shows the list once `pane-border-status` is set on it.

| Keys | Action |
| --- | --- |
| `C-q C-a` | Open a Claude Code tab: `claude --ide` in the session's root |
| `C-q C-t` | Open a shell tab in the pane's current directory |
| `C-q C-n` | Show the next tab, wrapping from the last to the first |
| `C-q C-p` | Show the previous tab |
| `C-q x`, then `y` | Close the shown tab and show its neighbor; on a pane without tabs, kill the pane |

- Keep Ctrl held for the second key: `C-q n` and `C-q p` switch windows
- A tab whose program exits closes like `C-q x`, so quitting a Claude
  Code tab opened with `C-q C-a`, or typing `exit` in a shell, closes its
  tab; the claude that `ide` starts drops to its shell
- A hidden tab keeps running, parked in the `tabs-store` session
- A pane removed any other way than `C-q x` or its program exiting, such
  as with `kill-window`, loses its hidden tabs the next time `tabs.sh`
  runs
- Tabs switch by key only, not by clicking the list

`tabs.sh` does the work behind these keys and the `pane-died` and
`pane-title-changed` hooks in `tmux.conf`; its header describes how a tab
is kept.

## Quitting a session

`C-q C-x`, then `y`, quits every program in the session with the keys its
user would type, so the session closes with its last pane: nvim gets
`:qa`, Claude Code Ctrl-D twice, and a shell Ctrl-D once. A pane whose
program exits drops to its shell, which is quit next, and a closed tab
brings the next tab of its slot into view, which is quit in turn.

- nvim stays while a buffer has unsaved changes, and bash while it has
  stopped jobs; the run quits the rest and names the panes left on the
  status line
- A second run sends that bash another Ctrl-D, which ends it with its
  stopped jobs, as a second Ctrl-D typed by hand does
- The run sends nothing more once a pane runs any other program, or a
  shell runs a command such as a script, and names that pane
- Claude Code exits on Ctrl-D twice even in the middle of a turn, so
  check that no Claude Code session is at work before answering `y`
