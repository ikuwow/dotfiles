-- Neovim as the whole IDE, as an overlay on the main config: a file tree on
-- the left, buffers as tabs, Claude Code on the right, and a shell terminal
-- at the bottom. bin/nvim-ide starts nvim with `-u` pointing here, so this
-- file runs in place of the main init.vim, sources it, and adds the IDE
-- parts on top. Plain nvim never reads this file.

local this = vim.fn.fnamemodify(debug.getinfo(1, "S").source:sub(2), ":p")
-- Appended, so the runtimepath keeps the main config's order
vim.opt.rtp:append(vim.fn.fnamemodify(this, ":h"))
-- -u leaves $MYVIMRC unset, and the main config sources it again after
-- installing plugins
vim.env.MYVIMRC = this

vim.cmd.source(vim.fn.stdpath("config") .. "/init.vim")

-- The main config's vim-plug list, extended. plug#end() places the plugins
-- added after the main config's own plug#end() on the runtimepath, and the
-- main config's VimEnter check installs any that are missing, then sources
-- $MYVIMRC, which the assignment above points at this file. The file tree
-- is the main config's fern.vim.
-- The added plugins live outside g:plug_home, where :PlugClean in plain
-- nvim, whose list lacks them, never looks.
local extra = {
  "nvim-tree/nvim-web-devicons",
  "akinsho/bufferline.nvim",
  "folke/edgy.nvim",
}
local extra_home = vim.fn.stdpath("data") .. "/plugged-nvim-ide/"
for _, repo in ipairs(extra) do
  vim.fn["plug#"](repo, { dir = extra_home .. repo:match("[^/]+$") })
end
vim.fn["plug#end"]()

for _, repo in ipairs(extra) do
  if vim.fn.isdirectory(vim.g.plugs[repo:match("[^/]+$")].dir) == 0 then
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

require("ide.terminal")
require("ide.plugins")
require("ide.keymaps")
require("ide.startup")
