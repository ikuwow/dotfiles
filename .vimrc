"=========================="
"-- Basic Configurations --"
"=========================="

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

" Disable providers except python3
let g:loaded_python_provider = 0
let g:loaded_ruby_provider = 0
let g:loaded_node_provider = 0
let g:loaded_perl_provider = 0

" Python3 configurations
let s:ostype = trim(system('uname -m'))
if s:ostype == 'arm64'
    let s:bin_prefix = '/opt/homebrew/bin/'
elseif s:ostype == 'x86_64'
    let s:bin_prefix = '/usr/local/bin/'
else
    echo 'Error: Unsupported ostype'
endif
let g:python3_host_prog = s:bin_prefix . 'python3'
if has("nvim")
    let s:pip3 = s:bin_prefix . 'pip3'
    " NOTE: It's temporarily disabled because it's slow
    " call system(s:pip3 . ' install neovim pynvim')
endif

"=====================================
"-- dein.vim Configulation Section --
"=====================================

if strlen($SSH_CLIENT) == 0

    " Install dein.vim
    if has("nvim")
        let s:dein_base = expand('~/.cache/dein_nvim')
    else
        let s:dein_base = expand('~/.cache/dein_vim')
    endif
    call mkdir(s:dein_base, 'p')

    if &runtimepath !~# '/dein.vim'
        let s:dein_src = s:dein_base . '/repos/github.com/Shougo/dein.vim'
        if !isdirectory(s:dein_src)
            echo "Cloning dein.vim..."
            execute '!git clone https://github.com/Shougo/dein.vim' s:dein_src
        endif
        execute 'set runtimepath+=' . substitute(s:dein_src, '[/\\]$', '', '')
    endif

    " dein.vim options
    let g:dein#auto_recache = v:true

    " Load dein.vim config
    let s:dein_toml = expand('~/.vim/dein/rc/dein.toml')
    let s:dein_toml_lazy = expand('~/.vim/dein/rc/dein_lazy.toml')

    if dein#load_state(s:dein_base)
        call dein#begin(s:dein_base)
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
        echo "Executing dein#install()..."
        call dein#install()
    endif

endif

" https://github.com/Shougo/dein.vim
filetype plugin indent on
syntax enable

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
