-- Terminal windows look as the programs in them look in Ghostty: the
-- colorscheme stays with the editor, and terminal windows take the
-- foreground, background, and 16-color palette of Ghostty's current theme.
-- Without ghostty on PATH, terminal windows keep the colorscheme's Normal
-- and nvim's own palette.

local ghostty = {}
if vim.fn.executable("ghostty") == 1 then
  for _, line in ipairs(vim.fn.systemlist({ "ghostty", "+show-config" })) do
    local key, color = line:match("^(%w+) = (#%x+)$")
    if key == "foreground" or key == "background" then
      ghostty[key] = color
    end
    local i, pcolor = line:match("^palette = (%d+)=(#%x+)$")
    if i and tonumber(i) <= 15 then
      -- nvim reads these on TermOpen
      vim.g["terminal_color_" .. i] = pcolor
    end
  end
end

-- Terminal windows map Normal to this group, since a cell with no color of
-- its own takes Normal's colors, which are the colorscheme's
local function set_group()
  vim.api.nvim_set_hl(0, "IdeTerminal", { fg = ghostty.foreground, bg = ghostty.background })
end
set_group()
vim.api.nvim_create_autocmd("ColorScheme", {
  group = vim.api.nvim_create_augroup("ide-terminal-colors", { clear = true }),
  callback = set_group,
})

-- The main config and its plugins highlight indentation, trailing spaces,
-- and full-width spaces in every window, which would paint over the
-- terminal programs' own drawing. Indent guides skip every buffer with a
-- 'buftype', terminals included, and the autocmd clears the other matches
-- once their autocmds have added them.
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
