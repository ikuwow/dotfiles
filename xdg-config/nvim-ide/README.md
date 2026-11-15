# nvim-ide

Neovim as the whole IDE: the main Neovim config (`xdg-config/nvim/init.lua`) with an overlay that adds a fixed layout around the editor, holding a file tree, buffers shown as tabs, Claude Code sessions, and a shell terminal.

```
+------------------------------------------------------+
| Files | buffer tabs (bufferline)                     |
+--------+----------------------------+----------------+
| Files  | editor area                | Claude Code 1/2|
| (fern) |                            | (claudecode)   |
|        +----------------------------+                |
|        | Terminal (snacks)          |                |
+--------+----------------------------+----------------+
```

## Starting

`nvim-ide [dir]` starts nvim in `dir`, the current directory by default, with `-u` pointing at this directory's `init.lua`. Plain `nvim` never reads this config.

The first start installs the three plugins the overlay adds, in a vim-plug window, and then opens the layout.

## Which plugin does what

| Part of the screen | Plugin |
| --- | --- |
| Fixed panel positions, and each panel's title bar | edgy.nvim |
| Tab row at the top, one tab per open buffer | bufferline.nvim |
| File tree on the left | fern.vim, from the main config |
| Claude Code on the right | claudecode.nvim, with `lua/ide/claude.lua` holding several sessions |
| Shell terminal at the bottom, file and grep pickers | snacks.nvim |
| Status line | lightline.vim, from the main config |
| Editor colors | the main config's `desert` |
| Terminal window colors | `lua/ide/terminal.lua`, from `ghostty +show-config` |

## Files and tabs

The tabs at the top are buffers, drawn by bufferline. A file opened in the editor area adds a tab, and the panels stay where they are when the tab changes.

| Action | Keys or mouse |
| --- | --- |
| Open a file | `o` or `Enter` in fern, `<Space><Space>` (find by name), `<Space>/` (grep), `:e path` |
| Switch tabs | click a tab, `<Space>,` (pick from a list), `:bnext` / `:bprevious` |
| Close a tab | click its `×`, right-click it, `<Space>bd`; each asks before dropping unsaved changes |
| Close every other tab | `<Space>bo` |

A Vim tab page (`:tabnew`, or `t` in fern) is a separate window layout and opens without the panels. Claude Code opens each diff in a tab page of its own, with the shown session beside it, so the panels in the first tab keep their sizes.

## Moving between windows

`<C-;>` then `h`, `j`, `k`, or `l` moves to the window on that side, from the editor, fern, or a terminal window, in Normal, Insert, or Terminal mode. `w` and `p` after `<C-;>` work as after `<C-w>`.

- A lone `<C-;>` leaves Insert or Terminal mode
- In the editor and fern, `<C-w>h` and the other `<C-w>` commands work as usual
- In Terminal mode, `<C-w>` goes to the program, where it deletes the word before the cursor
- `<C-;>` reaches nvim only from a terminal that speaks the CSI u key encoding; in Insert mode, `<C-v><C-;>` inserts the text `<C-;>` when it does, and `;` when it does not

## Panels

| Panel | Show or hide | Command-key alias |
| --- | --- | --- |
| Files (fern) | `<Space>e` | `<D-b>` |
| Terminal | `<Space>t` | `<D-o>` |
| Claude Code | `<Space>ac` to show or hide, `<Space>af` to focus, or to hide when focused | `<D-i>`, as `<Space>af` |

The `<Space>` keys work in Normal mode, and the Command-key aliases also in Terminal mode, inside a shell or Claude Code. The aliases reach nvim in Neovide, and in a terminal only when it reports Command to nvim and binds nothing to the key itself.

Clicking the triangle in a panel's title bar closes that panel, since each panel holds one window. The keys above bring it back, and a Claude Code session or a terminal keeps running while its panel is closed.

## Claude Code sessions

The right panel holds several sessions, one shown at a time, and its title shows which one (`2/3`). Every session connects to this nvim and can open diffs in it, and the selection and `@` mentions (`<Space>ab`, `<Space>as`) go to every session at once, hidden ones included.

| Action | Keys |
| --- | --- |
| New session | `<Space>an` |
| New session with `--resume` | `<Space>ar` |
| New session with `--continue` | `<Space>aC` |
| Next / previous session | `<Space>a]` / `<Space>a[` |
| Add the current file to the prompt | `<Space>ab` |
| Send the selection | `<Space>as` in Visual mode |
| Accept / deny a diff | `<Space>aa` / `<Space>ad` |

A session that exits with an error keeps its buffer, and the message names its number, so `:buffer N` shows its output.

## fern

fern's keys come from the main config.

| Action | Key |
| --- | --- |
| Open | `o`, `Enter` |
| Open in a vertical / horizontal split | `s` / `i` |
| New file or directory | `ma` |
| Show or hide hidden files | `I` |
| Reload | `r` |
| Close | `q` |

## Mouse

- Clicking a window focuses it, and clicking a tab switches to it
- Right-clicking a tab closes it, as clicking its `×` does
- Clicking a panel's title-bar triangle closes the panel (see Panels)

## Plugins on disk

The main config's plugins live in `~/.local/share/nvim/plugged`, and the three the overlay adds (bufferline, edgy, nvim-web-devicons) in `~/.local/share/nvim/plugged-nvim-ide`. `:PlugUpdate` in nvim-ide updates both. `:PlugClean` in plain nvim leaves the overlay's plugins alone.
