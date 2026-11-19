---
name: ide-open
description: Show a file to the user in their editor, the nvim pane beside Claude Code in an `ide` tmux session, with `ide --open`. Use when the user asks to show or open a file, or a line of one, in the editor or on the left, such as "Xを見せて", "Xを開いて", or "左で開いて".
---

# Open a file in the editor

Run `ide --open <file> [<line>]` from a directory inside the project.

- `<file>` is absolute or relative to the current directory, and `<line>` puts the cursor on that line
- The file opens in nvim's editor window beside the tree, and nvim's focus moves there
- `ide` finds the session from the current directory, so run it from inside the project the session belongs to
- When it exits non-zero, tell the user its error, since the file was not shown
  - `no ide session for <root>`: this Claude Code runs outside an `ide` session
  - `not listening on <socket>`: the session's nvim runs without the socket that `ide` starts it with, which a new session or restarting nvim with `nvim --listen <socket>` fixes
