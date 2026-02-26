"=========================="
"-- Basic Configurations --"
"=========================="

" Only Vim >= 8.0 and NeoVim are supported
if v:version < 800 && !has("nvim")
    echo "WARNING: This .vimrc/init.vim does not support your vim!"
    echo "Some functions may not work."
endif

autocmd!
set nocompatible " do not use vi compatible mode

set langmenu=en_US.UTF-8
set nu
set title " display filename (not Thank you for using Vim.)
set ruler " display ruler (60,7 13%)
set showcmd " show inputting key

set hlsearch " highlight the search word
set ignorecase
set smartcase

set clipboard=unnamed " sharing clipboard
if has('termguicolors')
    set termguicolors
endif
colorscheme desert
set ambiwidth=double

" indents and tabs
set shiftwidth=4
set autoindent
set expandtab " convert tab to spaces
set tabstop=4 " spaces number of tab
set tw=0 " text width
set breakindent
set formatoptions=q
autocmd FileType * setlocal formatoptions-=ro

set nobackup " do not create *~ files
set noundofile " do not create *.un~ files
set backupskip=/tmp/*,/private/tmp/*
set cmdheight=1
set virtualedit=block

" quickly edit .vimrc
command! Ev edit $MYVIMRC
command! Eg edit $MYGVIMRC
command! Sv source $MYVIMRC
command! Sg source $MYGVIMRC

" complement { after Enter
inoremap {<Enter> {}<Left><CR><ESC><S-o>

augroup HighlightTrailingSpaces
    autocmd!
    autocmd VimEnter,WinEnter,ColorScheme * highlight TrailingSpaces term=underline guibg=green ctermbg=green
    autocmd VimEnter,WinEnter * match TrailingSpaces /\s\+$/
augroup END

" quickly remove trailing whitespaces
fun! TrimTrailingWhitespaces()
    let l:save = winsaveview()
    %s/\s\+$//e
    call winrestview(l:save)
endfun
command! TrimTrailingWhitespaces call TrimTrailingWhitespaces()

" automatically apply .vimrc changes
augroup AutoReloadVimrc
    autocmd!
augroup END

if has('gui_running')
    autocmd AutoReloadVimrc BufWritePost $MYVIMRC source $MYVIMRC | if has('gui_running') | source $MYGVIMRC
    autocmd AutoReloadVimrc BufWritePost $MYGVIMRC if has ('gui_running') | source $MYGVIMRC
else
    autocmd AutoReloadVimrc BufWritePost $MYVIMRC nested source $MYVIMRC
endif

" Disable providers except python3
let g:loaded_python_provider = 0
let g:loaded_ruby_provider = 0
let g:loaded_node_provider = 0
let g:loaded_perl_provider = 0

" Python3 configurations
if executable('brew')
    let s:brew_prefix = trim(system('brew --prefix'))
    let s:bin_prefix = s:brew_prefix . '/bin/'
else
    echo 'Warning: `brew` not found. s:brew_prefix/s:bin_prefix is set empty.'
    let s:brew_prefix = ''
    let s:bin_prefix = ''
endif

let g:python3_host_prog = s:bin_prefix . 'python3'
if has("nvim")
    let s:pip3 = s:bin_prefix . 'pip3'
    call system(s:pip3 . ' install neovim pynvim')
endif

if strlen($SSH_CLIENT) != 0
    echo 'Your vim is over ssh, so no plugins are loaded.'
    finish
endif

" Install vim-plug
let data_dir = has('nvim') ? stdpath('data') . '/site' : '~/.vim'
if empty(glob(data_dir . '/autoload/plug.vim'))
    let s:vim_plug_url = 'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
    silent execute '!curl -fLo ' . data_dir . '/autoload/plug.vim --create-dirs ' . s:vim_plug_url
    autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

" Run PlugInstall if there are missing plugins
autocmd VimEnter * if len(filter(values(g:plugs), '!isdirectory(v:val.dir)'))
    \| PlugInstall --sync | source $MYVIMRC
    \| endif

call plug#begin()

Plug 'lambdalisue/fern.vim'
    let g:fern#default_hidden = 1
    command! Nt Fern . -toggle -drawer
    Plug 'lambdalisue/fern-git-status.vim' " It depends on fern.vim

" https://github.com/lambdalisue/vim-fern/wiki/Tips#define-nerdtree-like-mappings
function! s:init_fern() abort
  " Define NERDTree like mappings
  nmap <buffer> o <Plug>(fern-action-open:edit)
  nmap <buffer> go <Plug>(fern-action-open:edit)<C-w>p
  nmap <buffer> t <Plug>(fern-action-open:tabedit)
  nmap <buffer> T <Plug>(fern-action-open:tabedit)gT
  nmap <buffer> i <Plug>(fern-action-open:split)
  nmap <buffer> gi <Plug>(fern-action-open:split)<C-w>p
  nmap <buffer> s <Plug>(fern-action-open:vsplit)
  nmap <buffer> gs <Plug>(fern-action-open:vsplit)<C-w>p
  nmap <buffer> ma <Plug>(fern-action-new-path)
  nmap <buffer> P gg

  nmap <buffer> C <Plug>(fern-action-enter)
  nmap <buffer> u <Plug>(fern-action-leave)
  nmap <buffer> r <Plug>(fern-action-reload)
  nmap <buffer> R gg<Plug>(fern-action-reload)<C-o>
  nmap <buffer> cd <Plug>(fern-action-cd)
  nmap <buffer> CD gg<Plug>(fern-action-cd)<C-o>

  nmap <buffer> I <Plug>(fern-action-hidden-toggle)

  nmap <buffer> q :<C-u>quit<CR>
endfunction

augroup fern-custom
    autocmd! *
    autocmd FileType fern call s:init_fern()
augroup END

let g:ale_completion_enabled = 1 " This setting must be set before ALE is loaded.
Plug 'dense-analysis/ale'
    let g:ale_linters = {
    \    'html': ['htmlhint'],
    \    'php': ['php', 'phpcs'],
    \    'javascript': ['eslint'],
    \    'markdown': ['textlint']
    \}
    let g:ale_lint_on_text_changed = 'never'
    let g:ale_virtualtext_cursor = 0

Plug 'thinca/vim-zenspace'
    let g:zenspace#default_mode = 'on'
    augroup vimrc-highlight
        autocmd!
        autocmd ColorScheme * highlight ZenSpace ctermbg=Red guibg=Red
    augroup END

Plug 'tpope/vim-fugitive'

Plug 'itchyny/lightline.vim' " It depends on vim-fugitive
    let g:lightline = {
        \ 'colorscheme': 'jellybeans',
        \ 'active': {
        \     'left': [
        \         ['mode', 'current_branch', 'paste'],
        \         [ 'modified', 'filename', 'readonly']
        \     ]
        \ },
        \ 'component': {
        \     'readonly': '%{&readonly?"[RO]":""}'
        \ },
        \ 'component_function': {
        \     'current_branch': 'LLCurrentBranch',
        \     'filename': 'LLFileName',
        \     'mode': 'LLMultiMode',
        \     'fileformat': 'LLFileFormat',
        \     'filetype': 'LLFileType',
        \     'fileencoding': 'LLFileEncoding'
        \ }
    \ }

"-- lightline functions --"
function! LLCurrentBranch()
    try
        if exists('*fugitive#head') && strlen(fugitive#head())
            return "ト " . fugitive#head()
        endif
    catch
    endtry
    return ''
endfunction

function! LLFileName()
    return expand('%:t')
endfunction

function! LLMultiMode()
    let fname = expand('%:t')
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

Plug 'nathanaelkane/vim-indent-guides'
    let g:indent_guides_enable_on_vim_startup=1
    let g:indent_guides_start_level=2
    let g:indent_guides_color_change_percent = 2
    let g:indent_guides_guide_size = 1

Plug 'editorconfig/editorconfig-vim'
    let g:EditorConfig_max_line_indicator = "exceeding"

Plug 'vim-scripts/taglist.vim'
    let g:Tlist_Use_Right_Window = 1
    let g:Tlist_WinWidth = 40

Plug 'glidenote/memolist.vim'
    let g:memolist_path = expand("~/Documents/Memos")
    let g:memolist_memo_suffix = "md"

Plug 'previm/previm'
    let g:previm_open_cmd="open -a Safari"
    augroup PrevimSettings
        autocmd!
        autocmd BufNewFile,BufRead *.{md,mdwn,mkd,mkdn,mark*} set filetype=markdown
    augroup END

Plug 'tpope/vim-rhubarb'
Plug 'tomtom/tcomment_vim'
Plug 'airblade/vim-gitgutter'
Plug 'mattn/emmet-vim'
Plug 'junegunn/vim-easy-align'
Plug 'tpope/vim-surround'
" Plug 'github/copilot.vim'
"     let g:copilot_filetypes = {
"     \ 'gitcommit': v:true,
"     \ 'yaml': v:true
"     \ }
"     if s:brew_prefix != ''
"         let g:copilot_node_command = s:brew_prefix . '/opt/node@20/bin/node'
"     endif

" File specific
Plug 'KazuakiM/vim-sqlfix'
Plug 'cespare/vim-toml'
Plug 'hashivim/vim-terraform'
Plug 'othree/yajs.vim'
Plug 'mattn/vim-sqlfmt'
Plug 'fatih/vim-go', { 'do': 'GoUpdateBinaries' }
Plug 'chr4/nginx.vim'
Plug 'glench/vim-jinja2-syntax'
Plug 'pearofducks/ansible-vim'
Plug 'posva/vim-vue'
Plug 'bfontaine/Brewfile.vim'
Plug 'okkiroxx/rtx.vim'

if has('nvim')
    Plug 'kassio/neoterm'
endif

" This automatically executes `filetype plugin indent on` and `syntax enable`.
call plug#end()

" statusline config
set laststatus=2
