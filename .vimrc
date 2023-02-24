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

if strlen($SSH_CLIENT) == 0
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

    if has('nvim')
        Plug 'kassio/neoterm'
    endif

    Plug 'w0rp/ale'
    let g:ale_linters = {
    \    'html': ['htmlhint'],
    \    'php': ['php', 'phpcs'],
    \    'javascript': ['eslint'],
    \    'markdown': ['textlint']
    \}
    let g:ale_lint_on_text_changed = 'never'

    Plug 'airblade/vim-gitgutter'

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
        \     'current_branch': 'CurrentBranch',
        \     'filename': 'FileName',
        \     'mode': 'MultiMode',
        \     'fileformat': 'FileFormat',
        \     'filetype': 'FileType',
        \     'fileencoding': 'FileEncoding'
        \ }
    \ }

    "-- lightline functions --"
    function! CurrentBranch()
        try
            if exists('*fugitive#head') && strlen(fugitive#head())
                return "ト " . fugitive#head()
            endif
        catch
        endtry
        return ''
    endfunction

    function! FileName()
        return expand('%:t')
    endfunction

    function! MultiMode()
        let fname = expand('%:t')
        return lightline#mode()
    endfunction

    function! FileFormat()
        return winwidth(0) > 70 ? &fileformat : ''
    endfunction

    function! FileType()
        return winwidth(0) > 70 ? (&filetype !=# '' ? &filetype : 'no ft') : ''
    endfunction

    function! FileEncoding()
        return winwidth(0) > 70 ? (&fenc !=# '' ? &fenc : &enc) : ''
    endfunction


    Plug 'tpope/vim-rhubarb'

    Plug 'nathanaelkane/vim-indent-guides'
    let g:indent_guides_enable_on_vim_startup=1
    let g:indent_guides_start_level=2
    let g:indent_guides_color_change_percent = 2
    let g:indent_guides_guide_size = 1

    Plug 'editorconfig/editorconfig-vim'
    let g:EditorConfig_core_mode = 'python_external'
    let g:EditorConfig_max_line_indicator = "exceeding"

    Plug 'tomtom/tcomment_vim'

    Plug 'vim-scripts/taglist.vim'
    let g:Tlist_Use_Right_Window = 1
    let g:Tlist_WinWidth = 40

    Plug 'chr4/nginx.vim'

    Plug 'glench/vim-jinja2-syntax'

    Plug 'pearofducks/ansible-vim'

    Plug 'posva/vim-vue'

    Plug 'bfontaine/Brewfile.vim'

    Plug 'okkiroxx/rtx.vim'

    Plug 'glidenote/memolist.vim' " TODO: Install on CmdwinEnter
    let g:memolist_path = expand("~/Documents/Memos")
    let g:memolist_memo_suffix = "md"

    Plug 'mattn/emmet-vim'
    " on_event = ['InsertEnter']

    Plug 'previm/previm'
    " on_ft = ['markdown']
    let g:previm_open_cmd="open -a Safari"
    augroup PrevimSettings
        autocmd!
        autocmd BufNewFile,BufRead *.{md,mdwn,mkd,mkdn,mark*} set filetype=markdown
    augroup END

    Plug 'junegunn/vim-easy-align'
    " on_event = ['CmdwinEnter']

    Plug 'KazuakiM/vim-sqlfix'
    " on_event = ['CmdwinEnter']

    Plug 'cespare/vim-toml'
    " on_ft = ['toml']

    Plug 'hashivim/vim-terraform'
    " on_ft = ['terraform']

    Plug 'othree/yajs.vim'
    " on_ft = ['javascript', 'html']

    Plug 'mattn/vim-sqlfmt'
    " on_ft = ['sql']

    Plug 'fatih/vim-go'
    " on_ft = ['go']

    " This automatically executes `filetype plugin indent on` and `syntax enable`.
    call plug#end()
endif

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
