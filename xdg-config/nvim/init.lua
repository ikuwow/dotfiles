-- Basic settings are shared with Vim, which falls back to the same vimrc.
local core_vimrc = vim.fs.joinpath(vim.fs.dirname(vim.fn.stdpath('config')), 'vim', 'vimrc')
-- An error stops the vimrc at that line; pcall reports it and keeps the rest
-- of this file running.
local ok, err = pcall(vim.cmd.source, core_vimrc)
if not ok then
  vim.notify(err, vim.log.levels.ERROR)
end

-- $MYVIMRC points at this file, so the vimrc's own reload autocmd misses
-- writes to the shared vimrc. The group is joined without clearing, which
-- keeps that autocmd, and is created here when the vimrc stopped before
-- defining it.
vim.api.nvim_create_autocmd('BufWritePost', {
  group = vim.api.nvim_create_augroup('AutoReloadVimrc', { clear = false }),
  pattern = { core_vimrc, vim.fn.resolve(core_vimrc) },
  nested = true,
  command = 'source $MYVIMRC',
})

-- Disable providers except python3
vim.g.loaded_python_provider = 0
vim.g.loaded_ruby_provider = 0
vim.g.loaded_node_provider = 0
vim.g.loaded_perl_provider = 0

-- Python3 configurations
local bin_prefix = ''
if vim.fn.executable('brew') == 1 then
  bin_prefix = vim.trim(vim.fn.system({ 'brew', '--prefix' })) .. '/bin/'
else
  print('Warning: `brew` not found. bin_prefix is set empty.')
end

local nvim_venv = vim.fn.stdpath('data') .. '/python3-venv'
-- The shell form fails with a nonzero exit when a command is missing, where
-- the list form raises E475 and stops this file.
if vim.fn.filereadable(nvim_venv .. '/bin/python3') == 0 then
  vim.fn.system(bin_prefix .. 'python3 -m venv ' .. nvim_venv)
  vim.fn.system(nvim_venv .. '/bin/pip install pynvim')
end
vim.g.python3_host_prog = nvim_venv .. '/bin/python3'

if (vim.env.SSH_CLIENT or '') ~= '' then
  print('Your vim is over ssh, so no plugins are loaded.')
  return
end

-- Install vim-plug
local plug_vim = vim.fn.stdpath('data') .. '/site/autoload/plug.vim'
if vim.fn.filereadable(plug_vim) == 0 then
  vim.fn.system('curl -fLo ' .. plug_vim .. ' --create-dirs '
    .. 'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim')
  vim.api.nvim_create_autocmd('VimEnter', { command = 'PlugInstall --sync | source $MYVIMRC' })
end

-- Run PlugInstall if there are missing plugins
vim.api.nvim_create_autocmd('VimEnter', {
  callback = function()
    for _, plug in pairs(vim.g.plugs) do
      if vim.fn.isdirectory(plug.dir) == 0 then
        vim.cmd('PlugInstall --sync | source $MYVIMRC')
        return
      end
    end
  end,
})

local Plug = vim.fn['plug#']

vim.call('plug#begin')

Plug('lambdalisue/fern.vim')
vim.g['fern#default_hidden'] = 1
-- Every tab's drawer shows one shared fern buffer, so its expanded
-- directories stay the same across tabs
vim.g['fern#disable_drawer_tabpage_isolation'] = 1
vim.api.nvim_create_user_command('Nt', 'Fern . -toggle -drawer -reveal=%', {})
Plug('lambdalisue/fern-git-status.vim') -- It depends on fern.vim
-- File type icons need Nerd Font glyphs, which Ghostty draws from its
-- built-in Symbols Nerd Font regardless of font-family
Plug('lambdalisue/vim-nerdfont')
Plug('lambdalisue/vim-fern-renderer-nerdfont') -- It depends on vim-nerdfont
vim.g['fern#renderer'] = 'nerdfont'
vim.g['fern#renderer#nerdfont#indent_markers'] = 1
Plug('lambdalisue/vim-glyph-palette')
vim.api.nvim_create_autocmd('FileType', {
  group = vim.api.nvim_create_augroup('fern-glyph-palette', { clear = true }),
  pattern = 'fern',
  callback = function()
    vim.fn['glyph_palette#apply']()
  end,
})

-- Tabs share the drawer's visibility like an IDE's sidebar: entering a tab
-- opens or closes its drawer to match the tab just left.
-- A tab with a diff window, such as claudecode.nvim's diff tab, neither
-- follows nor leads, so the diff keeps its width and leaving it changes
-- nothing.
local function drawer_win(tabpage)
  for _, win in ipairs(vim.api.nvim_tabpage_list_wins(tabpage)) do
    if vim.api.nvim_buf_get_name(vim.api.nvim_win_get_buf(win)):match('^fern://drawer:') then
      return win
    end
  end
end
local function has_diff_win(tabpage)
  for _, win in ipairs(vim.api.nvim_tabpage_list_wins(tabpage)) do
    if vim.wo[win].diff then
      return true
    end
  end
  return false
end
-- Moves the drawer's cursor to the file and expands its parents, like an IDE
-- revealing the active file. Only a file under the working directory
-- qualifies, since "Fern ." roots the drawer there.
local function reveal_in_drawer(bufnr)
  if vim.bo[bufnr].buftype ~= '' then
    return
  end
  local path = vim.api.nvim_buf_get_name(bufnr)
  if not vim.startswith(path, vim.fn.getcwd() .. '/') then
    return
  end
  local win = drawer_win(0)
  if not win then
    return
  end
  vim.api.nvim_win_call(win, function()
    vim.cmd('FernReveal ' .. vim.fn.fnameescape(path))
  end)
end
vim.api.nvim_create_autocmd('BufEnter', {
  group = vim.api.nvim_create_augroup('fern-drawer-reveal', { clear = true }),
  callback = function(args)
    reveal_in_drawer(args.buf)
  end,
})
local drawer_in_left_tab
local drawer_sync = vim.api.nvim_create_augroup('fern-drawer-tab-sync', { clear = true })
vim.api.nvim_create_autocmd('TabLeave', {
  group = drawer_sync,
  callback = function()
    local tabpage = vim.api.nvim_get_current_tabpage()
    if has_diff_win(tabpage) then
      drawer_in_left_tab = nil
    else
      drawer_in_left_tab = drawer_win(tabpage) ~= nil
    end
  end,
})
vim.api.nvim_create_autocmd('TabEnter', {
  group = drawer_sync,
  callback = function()
    local want = drawer_in_left_tab
    -- Deferred, so a new tab has loaded its file and set up its diff first
    vim.schedule(function()
      local tabpage = vim.api.nvim_get_current_tabpage()
      if want == nil or has_diff_win(tabpage) then
        return
      end
      local win = drawer_win(tabpage)
      if want and not win then
        vim.cmd('Fern . -drawer -stay')
        reveal_in_drawer(0)
      elseif not want and win and #vim.api.nvim_tabpage_list_wins(tabpage) > 1 then
        vim.api.nvim_win_close(win, false)
      end
    end)
  end,
})

vim.g.ale_completion_enabled = 1 -- This setting must be set before ALE is loaded.
Plug('dense-analysis/ale')
vim.g.ale_linters = {
  html = { 'htmlhint' },
  php = { 'php', 'phpcs' },
  javascript = { 'eslint' },
  markdown = { 'textlint' },
}
vim.g.ale_lint_on_text_changed = 'never'
vim.g.ale_virtualtext_cursor = 0

Plug('thinca/vim-zenspace')
vim.g['zenspace#default_mode'] = 'on'
vim.api.nvim_create_autocmd('ColorScheme', {
  group = vim.api.nvim_create_augroup('vimrc-highlight', { clear = true }),
  command = 'highlight ZenSpace ctermbg=Red guibg=Red',
})

Plug('tpope/vim-fugitive')

Plug('itchyny/lightline.vim') -- It depends on vim-fugitive
vim.g.lightline = {
  colorscheme = 'jellybeans',
  active = {
    left = {
      { 'mode', 'current_branch', 'paste' },
      { 'modified', 'filename', 'readonly' },
    },
  },
  component = {
    readonly = '%{&readonly?"[RO]":""}',
  },
  component_function = {
    current_branch = 'LLCurrentBranch',
    filename = 'LLFileName',
    mode = 'LLMultiMode',
    fileformat = 'LLFileFormat',
    filetype = 'LLFileType',
    fileencoding = 'LLFileEncoding',
  },
}

-- lightline#init() calls each component function once with call(), which
-- rejects v:lua names, so these are Vimscript functions.
vim.cmd([[
function! LLCurrentBranch()
    try
        if exists('*FugitiveHead') && strlen(FugitiveHead())
            return "ト " . FugitiveHead()
        endif
    catch
    endtry
    return ''
endfunction

function! LLFileName()
    return expand('%:t')
endfunction

function! LLMultiMode()
    return lightline#mode()
endfunction

function! LLFileFormat()
    return winwidth(0) > 70 ? &fileformat : ''
endfunction

function! LLFileType()
    return winwidth(0) > 70 ? (&filetype !=# '' ? &filetype : 'no ft') : ''
endfunction

function! LLFileEncoding()
    return winwidth(0) > 70 ? (&fenc !=# '' ? &fenc : &enc) : ''
endfunction
]])

Plug('nathanaelkane/vim-indent-guides')
vim.g.indent_guides_enable_on_vim_startup = 1
vim.g.indent_guides_start_level = 2
vim.g.indent_guides_color_change_percent = 2
vim.g.indent_guides_guide_size = 1

Plug('editorconfig/editorconfig-vim')
vim.g.EditorConfig_max_line_indicator = 'exceeding'

Plug('vim-scripts/taglist.vim')
vim.g.Tlist_Use_Right_Window = 1
vim.g.Tlist_WinWidth = 40

Plug('glidenote/memolist.vim')
vim.g.memolist_path = vim.fn.expand('~/Documents/Memos')
vim.g.memolist_memo_suffix = 'md'

Plug('previm/previm')
vim.g.previm_open_cmd = 'open'
vim.g.previm_enable_realtime = 1
vim.api.nvim_create_autocmd({ 'BufNewFile', 'BufRead' }, {
  group = vim.api.nvim_create_augroup('PrevimSettings', { clear = true }),
  pattern = '*.{md,mdwn,mkd,mkdn,mark*}',
  command = 'set filetype=markdown',
})

Plug('tpope/vim-rhubarb')
Plug('tomtom/tcomment_vim')
Plug('airblade/vim-gitgutter')
Plug('mattn/emmet-vim')
Plug('junegunn/vim-easy-align')
Plug('tpope/vim-surround')

-- File specific
Plug('KazuakiM/vim-sqlfix')
Plug('cespare/vim-toml')
Plug('hashivim/vim-terraform')
Plug('othree/yajs.vim')
Plug('mattn/vim-sqlfmt')
Plug('fatih/vim-go', { ['do'] = 'GoUpdateBinaries' })
Plug('chr4/nginx.vim')
Plug('glench/vim-jinja2-syntax')
Plug('pearofducks/ansible-vim')
Plug('posva/vim-vue')
Plug('bfontaine/Brewfile.vim')
Plug('okkiroxx/rtx.vim')

Plug('kassio/neoterm')
Plug('folke/snacks.nvim')
Plug('coder/claudecode.nvim')
-- Neovide IME inline preedit; self-detects Neovide, no-op in terminal nvim
Plug('sevenc-nanashi/neov-ime.nvim')

-- This automatically executes `filetype plugin indent on` and `syntax enable`.
vim.call('plug#end')

local ok, claudecode = pcall(require, 'claudecode')
if ok then
  claudecode.setup({
    diff_opts = {
      vertical_split = false,
      open_in_current_tab = false,
    },
  })
end

-- statusline config
vim.o.laststatus = 2
