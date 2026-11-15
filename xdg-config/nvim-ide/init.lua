-- Neovim as the whole IDE: a file tree on the left, buffers as tabs, Claude
-- Code on the right, and a shell terminal at the bottom. bin/nvim-ide starts
-- nvim with NVIM_APPNAME=nvim-ide to load this config.

vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

vim.opt.number = true
vim.opt.mouse = "a"
vim.opt.clipboard = "unnamed"
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.tabstop = 4
vim.opt.breakindent = true
vim.opt.virtualedit = "block"
vim.opt.undofile = false
-- One statusline for the whole screen, and splits that keep the text in
-- place, as edgy.nvim asks for
vim.opt.laststatus = 3
vim.opt.splitkeep = "screen"

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.uv.fs_stat(lazypath) then
  local out = vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "--branch=stable",
    "https://github.com/folke/lazy.nvim.git",
    lazypath,
  })
  if vim.v.shell_error ~= 0 then
    vim.api.nvim_echo({
      { "Failed to clone lazy.nvim:\n", "ErrorMsg" },
      { out, "WarningMsg" },
    }, true, {})
    return
  end
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  spec = { { import = "plugins" } },
  -- The config directory is this repository, so the lockfile lives with the
  -- installed plugins instead
  lockfile = vim.fn.stdpath("data") .. "/lazy-lock.json",
  install = { missing = true },
  checker = { enabled = false },
  change_detection = { notify = false },
})

require("ide.keymaps")
require("ide.startup")
