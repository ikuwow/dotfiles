"=========================="
"-- Basic Configurations --"
"=========================="

autocmd!
set nocompatible " do not use vi compatible mode

lang en_US.UTF-8
set nu
set title " display filename (not Thank you for using Vim.)
set ruler " display ruler (60,7 13%)
set showcmd " show inputting key
filetype plugin indent on

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
if version >=800 || has("nvim")
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
set virtualedit=block

augroup HighlightTrailingSpaces
    autocmd!
    autocmd VimEnter,WinEnter,ColorScheme * highlight TrailingSpaces term=underline guibg=green ctermbg=green
    autocmd VimEnter,WinEnter * match TrailingSpaces /\s\+$/
augroup END

" complement { after Enter
inoremap {<Enter> {}<Left><CR><ESC><S-o>

let g:python_host_prog = '/usr/local/bin/python'
let g:python3_host_prog = '/usr/local/bin/python3'

"=====================================
"-- dein.vim Configulation Section --
"=====================================
let s:dein_dir = expand('~/.vim/dein')
let s:dein_repo = s:dein_dir . '/repos/github.com/Shougo/dein.vim'
let s:dein_toml = s:dein_dir . '/rc/dein.toml'
let s:dein_toml_lazy = s:dein_dir . '/rc/dein_lazy.toml'

if !isdirectory(s:dein_repo) && strlen($SSH_CLIENT) == 0
    echo "Cloning dein.vim..."
    call system('git clone https://github.com/Shougo/dein.vim ' . shellescape(s:dein_repo))
    if v:shell_error != 0
        echo "Error while cloning dein.vim."
    end
endif

if isdirectory(s:dein_repo)
    if has('vim_starting')
        execute "set runtimepath+=" . s:dein_repo
    endif
    if dein#load_state(s:dein_dir)
        call dein#begin(s:dein_dir)
        if filereadable(s:dein_toml)
            call dein#load_toml(s:dein_toml)
        endif
        if filereadable(s:dein_toml_lazy)
            call dein#load_toml(s:dein_toml_lazy, {'lazy': 1})
        endif
        call dein#end()
        call dein#save_state()
    endif
    if has('vim_starting') && dein#check_install()
        call dein#install()
    endif
endif

syntax enable " なぜかこの辺に書かないと動かない

set laststatus=2
set t_Co=256

" quickly edit .vimrc
command! Ev edit $MYVIMRC
command! Eg edit $MYGVIMRC
command! Sv source $MYVIMRC
command! Sg source $MYGVIMRC

" quickly remove trailing whitespaces
fun! TrimTrailingWhitespaces()
    let l:save = winsaveview()
    %s/\s\+$//e
    call winrestview(l:save)
endfun
command! TrimTrailingWhitespaces call TrimTrailingWhitespaces()

" automatically apply .vimrc changes
augroup MyAutoCmd
    autocmd!
augroup END

if has('gui_running')
    autocmd MyAutoCmd BufWritePost $MYVIMRC source $MYVIMRC | if has('gui_running') | source $MYGVIMRC
    autocmd MyAutoCmd BufWritePost $MYGVIMRC if has ('gui_running') | source $MYGVIMRC
else
    autocmd MyAutoCmd BufWritePost $MYVIMRC nested source $MYVIMRC
endif
