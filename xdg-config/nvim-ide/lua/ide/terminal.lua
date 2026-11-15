-- Terminal windows look as the programs in them look in Ghostty: the
-- colorscheme stays with the editor, and terminal windows take Ghostty's
-- default colors and palette.

-- An empty group in place of Normal leaves the cells at the terminal's
-- default foreground and background
vim.api.nvim_set_hl(0, "IdeTerminal", {})
vim.api.nvim_create_autocmd("ColorScheme", {
  group = vim.api.nvim_create_augroup("ide-terminal-colors", { clear = true }),
  callback = function()
    vim.api.nvim_set_hl(0, "IdeTerminal", {})
  end,
})

-- The 16-color palette of Ghostty's current theme, which nvim reads on
-- TermOpen; nvim uses its own palette when ghostty is not on PATH
if vim.fn.executable("ghostty") == 1 then
  for _, line in ipairs(vim.fn.systemlist({ "ghostty", "+show-config" })) do
    local i, color = line:match("^palette = (%d+)=(#%x+)$")
    if i and tonumber(i) <= 15 then
      vim.g["terminal_color_" .. i] = color
    end
  end
end

-- <C-\> then h, j, k, l, w, or p leaves Terminal mode for that <C-w>
-- window command. <C-w> itself stays with the program, as a shell's and
-- Claude Code's word deletion, since a word typed right after it would
-- otherwise run as Normal-mode commands in another window. <C-\> is the
-- key nvim already uses to leave Terminal mode (<C-\><C-n>).
for _, key in ipairs({ "h", "j", "k", "l", "w", "p" }) do
  vim.keymap.set("t", "<C-\\>" .. key, "<C-\\><C-n><C-w>" .. key, { desc = "Window command " .. key })
end

-- The main config and its plugins highlight indentation, trailing spaces,
-- and full-width spaces in every window, which would paint over the
-- terminal programs' own drawing. Indent guides skip terminal buffers
-- outright, and the autocmd clears the other matches once their autocmds
-- have added them.
vim.g.indent_guides_exclude_buftype = 1
vim.api.nvim_create_autocmd({ "TermOpen", "BufWinEnter", "WinEnter" }, {
  group = vim.api.nvim_create_augroup("ide-terminal-windows", { clear = true }),
  callback = function()
    vim.schedule(function()
      if vim.bo.buftype ~= "terminal" then
        return
      end
      vim.fn.clearmatches()
      -- Panels get the same colors through edgy.nvim's window options
      if not require("edgy").get_win() then
        -- Local to this window and buffer, so a file opened in the window
        -- later keeps the colorscheme
        vim.wo[0][0].winhighlight = "Normal:IdeTerminal,NormalNC:IdeTerminal"
      end
    end)
  end,
})
