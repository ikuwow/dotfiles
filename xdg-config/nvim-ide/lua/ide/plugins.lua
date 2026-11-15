-- Setup of the plugins the IDE layout uses. fern.vim, snacks.nvim, and
-- claudecode.nvim come from the main config's plugin list; init.lua adds the
-- rest.

-- snacks.nvim refuses a second setup(), which sourcing $MYVIMRC again runs
if not require("snacks").did_setup then
  require("snacks").setup({
    bigfile = { enabled = true },
    picker = { enabled = true },
  })
end

vim.g["fern#drawer_width"] = 32

require("bufferline").setup({
  options = {
    close_command = function(buf)
      Snacks.bufdelete(buf)
    end,
    -- Right-click closes a tab as its × does, asking before it drops
    -- unsaved changes, in place of bufferline's default :bdelete!
    right_mouse_command = function(buf)
      Snacks.bufdelete(buf)
    end,
    always_show_bufferline = true,
    offsets = {
      { filetype = "fern", text = "Files", separator = true },
    },
  },
})

-- The main config's setup() has started the server, so this one only
-- replaces the terminal and diff settings
require("claudecode").setup({
  auto_start = false,
  terminal = {
    provider = require("ide.claude"),
    split_side = "right",
    split_width_percentage = 0.4,
  },
  -- A diff opens in a tab of its own, so the panels around the editor keep
  -- their sizes
  diff_opts = {
    layout = "horizontal",
    open_in_new_tab = true,
  },
})

-- Fixed panels around the editor area: the file tree on the left, Claude Code
-- on the right, and shell terminals at the bottom. A split or a help window
-- opened in the editor area leaves the panels where they are.
local function snacks_at(pos)
  return function(_, win)
    local w = vim.w[win].snacks_win
    return w ~= nil and w.position == pos and w.relative == "editor"
  end
end

-- edgy.nvim's default maps Normal to NormalFloat, a popup color in the
-- main colorscheme; the file tree keeps the editor's Normal, and terminal
-- panels take Ghostty's colors (see ide/terminal.lua)
local winbar_hl = "WinBar:EdgyWinBar,WinBarNC:EdgyWinBarNC"
local terminal_wo = { winhighlight = winbar_hl .. ",Normal:IdeTerminal,NormalNC:IdeTerminal" }

require("edgy").setup({
  left = {
    { title = "Files", ft = "fern" },
  },
  right = {
    { title = "Claude Code %{v:lua.require'ide.claude'.label()}", ft = "claudecode", wo = terminal_wo },
  },
  bottom = {
    {
      title = "Terminal %{b:snacks_terminal.id}",
      ft = "snacks_terminal",
      filter = snacks_at("bottom"),
      wo = terminal_wo,
    },
  },
  wo = { winhighlight = winbar_hl },
  options = {
    left = { size = 32 },
    right = {
      size = function()
        return math.floor(vim.o.columns * 0.4)
      end,
    },
    bottom = {
      size = function()
        return math.floor(vim.o.lines * 0.3)
      end,
    },
  },
  animate = { enabled = false },
})
