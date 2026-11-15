-- Neovim as the whole IDE, as an overlay on the main config: a file tree on
-- the left, buffers as tabs, Claude Code on the right, and a shell terminal
-- at the bottom. bin/nvim-ide starts nvim with `-u` pointing here, so this
-- file runs in place of the main init.vim, sources it, and adds the IDE
-- parts on top. Plain nvim never reads this file.

local this = vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":p")
vim.opt.rtp:prepend(vim.fn.fnamemodify(this, ":h"))
-- -u leaves $MYVIMRC unset, and the main config sources it again after
-- installing plugins
vim.env.MYVIMRC = this

vim.cmd.source(vim.fn.stdpath("config") .. "/init.vim")

-- The main config's vim-plug list, extended. plug#end() places the plugins
-- added after the main config's own plug#end() on the runtimepath, and the
-- main config's VimEnter check installs any that are missing, then sources
-- $MYVIMRC, which -u makes this file.
local extra = {
  { "nvim-lua/plenary.nvim" },
  { "MunifTanjim/nui.nvim" },
  { "nvim-tree/nvim-web-devicons" },
  { "nvim-neo-tree/neo-tree.nvim", { branch = "v3.x" } },
  { "akinsho/bufferline.nvim" },
  { "folke/edgy.nvim" },
}
for _, plug in ipairs(extra) do
  vim.fn["plug#"](plug[1], plug[2] or vim.empty_dict())
end
vim.fn["plug#end"]()

for _, plug in ipairs(extra) do
  local name = plug[1]:match("[^/]+$")
  if vim.fn.isdirectory(vim.g.plugs[name].dir) == 0 then
    return
  end
end

-- One statusline for the whole screen, and splits that keep the text in
-- place, as edgy.nvim asks for
vim.opt.laststatus = 3
vim.opt.splitkeep = "screen"
-- Box-drawing characters take one cell, as Claude Code and other terminal
-- programs draw them, and as the floating-window borders of snacks.nvim's
-- picker need; the main config's ambiwidth=double makes them two
vim.opt.ambiwidth = "single"
-- bufferline.nvim draws the tabline, so lightline keeps to the statusline
vim.g.lightline = vim.tbl_extend("force", vim.g.lightline, {
  enable = { statusline = 1, tabline = 0 },
})

-- The main config highlights indentation, trailing spaces, and full-width
-- spaces in every window, which would paint over the terminal programs'
-- own drawing, so terminal windows drop those matches once the main
-- config's autocmds have added them
vim.g.indent_guides_exclude_buftype = 1
vim.api.nvim_create_autocmd({ "TermOpen", "BufWinEnter", "WinEnter" }, {
  group = vim.api.nvim_create_augroup("ide-terminal-matches", { clear = true }),
  callback = function()
    vim.schedule(function()
      if vim.bo.buftype == "terminal" then
        vim.fn.clearmatches()
      end
    end)
  end,
})

require("ide.plugins")
require("ide.keymaps")
require("ide.startup")
