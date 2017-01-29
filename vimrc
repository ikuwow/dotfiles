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
    call dein#add('scrooloose/nerdtree')
    call dein#add('scrooloose/syntastic.git')
    call dein#add('kannokanno/previm')
    call dein#add('scrooloose/nerdtree')
    call dein#add('tpope/vim-fugitive') "git commands on vim
    call dein#add('mhinz/vim-startify') " startpage of vim
    call dein#add('terryma/vim-multiple-cursors')
    call dein#add('tomtom/tcomment_vim')
    call dein#add('mattn/emmet-vim')
    call dein#add('wakatime/vim-wakatime')
    call dein#add('Shougo/unite.vim')
    call dein#add('airblade/vim-gitgutter')
    call dein#add('editorconfig/editorconfig-vim')
    call dein#add('hashivim/vim-terraform')
    call dein#add('vim-scripts/taglist.vim')
    call dein#add('thinca/vim-zenspace') " hightlight full-width space like this 　
    call dein#add('glidenote/memolist.vim')
    call dein#add('Shougo/neocomplete')
    call dein#add('itchyny/lightline.vim')
    call dein#add('nathanaelkane/vim-indent-guides')
    call dein#end()
    call dein#save_state()
endif
if dein#check_install()
    call dein#install()
endif

syntax on " なぜかこの辺に書かないと動かない

" NERDTree
let NERDTreeShowHidden = 1
command! Nt NERDTree

" syntastic
let g:syntastic_php_checkers = ['php'] " do not use phpmd and phpcs
let g:syntastic_javascript_checkers = ['jshint']
let g:syntastic_html_tidy_exec = 'tidy5'
let g:syntastic_eruby_ruby_quiet_messages =
    \ {'regex': 'possibly useless use of a variable in void context'}
let g:syntastic_html_tidy_ignore_errors=[
    \'proprietary attribute "ng-'
\]

" previm
let g:previm_open_cmd="open -a Safari"
augroup PrevimSettings
    autocmd!
    autocmd BufNewFile,BufRead *.{md,mdwn,mkd,mkdn,mark*} set filetype=markdown
augroup END

" zenspace
let g:zenspace#default_mode = 'on'
augroup vimrc-highlight
    autocmd!
    autocmd ColorScheme * highlight ZenSpace ctermbg=Red guibg=Red
augroup END

" indent guides
let g:indent_guides_enable_on_vim_startup=1
let g:indent_guides_start_level=2
let g:indent_guides_color_change_percent =5
let g:indent_guides_guide_size = 1

" memolist
let g:memolist_path = expand("~/Documents/Memos")
let g:memolist_memo_suffix = "md"
let g:memolist_ex_cmd = 'NERDTree'

" neocomplete
let g:neocomplete#enable_at_startup = 1

" lightline
set laststatus=2 "ステータスラインを常時表示させる
set t_Co=256
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
        if &ft !~? 'nerdtree' && exists('*fugitive#head') && strlen(fugitive#head())
            return "ト " . fugitive#head()
        endif
    catch
    endtry
    return ''
endfunction

function! FileName()
    if &ft !~? 'nerdtree'
        return expand('%:t')
    endif
    return ''
endfunction

function! MultiMode()
    let fname = expand('%:t')
    return fname =~ 'NERD_tree' ? 'NERDTree' : lightline#mode()
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

