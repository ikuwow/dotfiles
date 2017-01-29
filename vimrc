"=========================="
"-- Basic Configurations --"
"=========================="
set nocompatible " do not use vi compatible mode

set nu
set title " display filename (not Thank you for using Vim.)
set ruler " display ruler (60,7 13%)
set showcmd " show inputting key
filetype  plugin indent on

set hlsearch " highlight the search word
set ic " ignore case

set clipboard=unnamed " sharing clipboard
colorscheme desert

" indents and tabs
set shiftwidth=4
set autoindent
set expandtab " convert tab to spaces
set tabstop=4 " spaces number of tab
set tw=0 " text width
if version >=800
    set breakindent
endif
set formatoptions=q
autocmd FileType * setlocal formatoptions-=ro

set nobackup " do not create *~ files
if version >= 703
    set noundofile " do not create *.un~ files
endif
set backupskip=/tmp/*,/private/tmp/*
set cmdheight=1

augroup HighlightTrailingSpaces
  autocmd!
  autocmd VimEnter,WinEnter,ColorScheme * highlight TrailingSpaces term=underline guibg=green ctermbg=green
autocmd VimEnter,WinEnter * match TrailingSpaces /\s\+$/
augroup END

" complement { after Enter
inoremap {<Enter> {}<Left><CR><ESC><S-o>

"=====================================
"-- dein.vim Configulation Section --
"=====================================
let s:dein_dir = expand('~/.vim/dein')
let s:dein_repo = s:dein_dir . '/repos/github.com/Shougo/dein.vim'
if !isdirectory(s:dein_repo)
    finish
endif

if has('vim_starting')
    execute "set runtimepath+=" . s:dein_repo
endif

if dein#load_state(s:dein_dir)
    call dein#begin(s:dein_dir)
    call dein#load_toml(s:dein_dir . '/rc/dein.toml')
    call dein#load_toml(s:dein_dir . '/rc/dein_lazy.toml')
    call dein#end()
    call dein#save_state()
endif
if dein#check_install()
    call dein#install()
endif

syntax enable " なぜかこの辺に書かないと動かない

set laststatus=2
set t_Co=256
