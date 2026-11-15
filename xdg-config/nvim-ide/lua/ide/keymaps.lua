-- Panel keys. Space-leader keys in Normal mode are the ones to rely on.
-- The Command-key aliases also work in terminal mode, where a shell or Claude
-- Code has every Ctrl key; they reach nvim in Neovide, and in a terminal only
-- when it reports Command to nvim and binds no action to the key itself.

local function shell()
  Snacks.terminal.toggle(nil, {
    -- A login shell, as Ghostty starts, since the exported PROMPT_COMMAND
    -- calls functions that only .bash_profile defines
    shell = { vim.o.shell, "-l" },
    env = require("ide.env").child(),
    win = { position = "bottom", height = 0.3 },
  })
end

local function tree()
  vim.cmd("Neotree toggle reveal")
end

local function claude()
  vim.cmd("ClaudeCodeFocus")
end

vim.keymap.set("n", "<leader>t", shell, { desc = "Toggle terminal" })

vim.keymap.set({ "n", "t" }, "<D-b>", tree, { desc = "File tree" })
vim.keymap.set({ "n", "t" }, "<D-i>", claude, { desc = "Focus Claude" })
vim.keymap.set({ "n", "t" }, "<D-o>", shell, { desc = "Toggle terminal" })
