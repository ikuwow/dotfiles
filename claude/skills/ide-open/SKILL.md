---
name: ide-open
description: Show a file to the user in their editor, the nvim pane beside Claude Code in an `ide` tmux session, with `ide --open`, and run other editor operations, such as opening a second file in a split, through `ide --socket`. Use whenever a file or a passage of one is to be shown to the user, including code you are about to quote while explaining, reviewing, or reporting on it, and when the user asks to show or open a file in the editor or on the left, such as "Xを見せて", "Xを開いて", or "左で開いて", or to arrange what that editor shows.
---

# Open a file in the editor

Show a file or a passage of one in the editor rather than pasting it into the conversation, and refer to it there by path and line, since the user reads it beside the conversation with the whole file around it. When `ide --open` fails with `no ide session`, show it in the conversation instead.

Run `ide --open <file> [<line>]` from a directory inside the project.

- `<file>` is absolute or relative to the current directory, and `<line>` puts the cursor on that line
- The file opens in nvim's editor window beside the tree, and nvim's focus moves there
- `ide` opens the file in the nvim of the session that belongs to the project of the current directory, whichever pane runs it, so run it from inside the project the user is looking at
- When it exits non-zero, tell the user its error, since the file was not shown, except for `no ide session` on a file you chose to show, which the conversation shows instead
  - `no ide session for <root>`: no `ide` session exists for the project of the current directory, either because this Claude Code runs outside one or because the current directory belongs to another project
  - `not listening on <socket>`: the session's nvim runs without the socket that `ide` starts it with, which a new session or restarting nvim with `nvim --listen <socket>` fixes
  - `did not answer in 5 seconds`: a prompt in the nvim pane, such as `Press ENTER`, waits for input, so ask the user to answer it and then run the command again

# Other operations in the editor

For anything beyond showing one file, such as opening a second file in a split, run `ide --socket` from inside the project, then pass the path it prints to `nvim --server`.

```
timeout 5 nvim --server <socket> --remote-expr 'execute(["belowright split /abs/path/to/bin/ide", "42"])'
```

- `execute()` runs the Ex commands in nvim's current window and returns their output, and the first one that fails makes the client exit non-zero with its error, leaving the effects of the commands before it, so prefer it over `--remote-send`, which types keys and reports nothing
- The current window can be the tree, so run `ide --open` first when the operation should act on the editor window
- Give file paths in an Ex command as absolute paths, since a relative one is read against the current window's directory, which the tree changes, and a path that names no file opens an empty buffer without an error
- `ide --socket` fails on the same session and socket errors as `ide --open`, and `timeout 5` exits 124 on the same prompt as `did not answer in 5 seconds`
- When nvim exited without removing its socket file, `ide --socket` still prints the path, and `nvim --server` then fails with `E247 ... connection refused`, which a new session fixes
