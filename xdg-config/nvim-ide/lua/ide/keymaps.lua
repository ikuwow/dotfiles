-- IDE keys. They start with a literal <Space> rather than <Leader>, since the
-- main config leaves <Leader> at its default and its plugins map under it.
-- The Command-key aliases also work in terminal mode, where a shell or Claude
-- Code has every Ctrl key; they reach nvim in Neovide, and in a terminal only
-- when it reports Command to nvim and binds no action to the key itself.

local map = vim.keymap.set

local function shell()
  Snacks.terminal.toggle(nil, {
    -- A login shell, as Ghostty starts, since the exported PROMPT_COMMAND
    -- calls functions from .functions, which only .bash_profile sources
    shell = { vim.o.shell, "-l" },
    win = {
      position = "bottom",
      height = 0.3,
      -- Ghostty's colors, as ide/terminal.lua gives every terminal window
      wo = { winhighlight = "Normal:IdeTerminal,NormalNC:IdeTerminal" },
    },
  })
end

local function tree()
  local file = vim.bo.buftype == "" and vim.fn.expand("%:p") or ""
  vim.cmd("Fern . -drawer -toggle" .. (file ~= "" and (" -reveal=" .. vim.fn.fnameescape(file)) or ""))
end

local function claude()
  vim.cmd("ClaudeCodeFocus")
end

local function session(f, ...)
  local args = { ... }
  return function()
    require("ide.claude")[f](unpack(args))
  end
end

-- Panels
map("n", "<Space>e", tree, { desc = "File tree" })
map("n", "<Space>t", shell, { desc = "Toggle terminal" })
map({ "n", "t" }, "<D-b>", tree, { desc = "File tree" })
map({ "n", "t" }, "<D-i>", claude, { desc = "Focus Claude" })
map({ "n", "t" }, "<D-o>", shell, { desc = "Toggle terminal" })

-- Pickers and buffers
map("n", "<Space><Space>", function() Snacks.picker.files() end, { desc = "Find files" })
map("n", "<Space>/", function() Snacks.picker.grep() end, { desc = "Grep" })
map("n", "<Space>,", function() Snacks.picker.buffers() end, { desc = "Buffers" })
map("n", "<Space>bd", function() Snacks.bufdelete() end, { desc = "Delete buffer" })
map("n", "<Space>bo", function() Snacks.bufdelete.other() end, { desc = "Delete other buffers" })

-- Claude Code
map("n", "<Space>ac", "<cmd>ClaudeCode<cr>", { desc = "Toggle Claude" })
map("n", "<Space>af", "<cmd>ClaudeCodeFocus<cr>", { desc = "Focus Claude" })
map("n", "<Space>an", session("new"), { desc = "New Claude session" })
map("n", "<Space>ar", session("new", "--resume"), { desc = "Resume in a new session" })
map("n", "<Space>aC", session("new", "--continue"), { desc = "Continue in a new session" })
map("n", "<Space>a]", session("cycle", 1), { desc = "Next Claude session" })
map("n", "<Space>a[", session("cycle", -1), { desc = "Previous Claude session" })
map("n", "<Space>ab", "<cmd>ClaudeCodeAdd %<cr>", { desc = "Add current buffer" })
map("v", "<Space>as", "<cmd>ClaudeCodeSend<cr>", { desc = "Send to Claude" })
map("n", "<Space>aa", "<cmd>ClaudeCodeDiffAccept<cr>", { desc = "Accept diff" })
map("n", "<Space>ad", "<cmd>ClaudeCodeDiffDeny<cr>", { desc = "Deny diff" })
