"=========================="
"-- Basic Configurations --"
"=========================="
set nocompatible " do not use vi compatible mode

set nu
set title " display filename (not Thank you for using Vim.)
set ruler " display ruler (60,7 13%)
set showcmd " show inputting key
filetype plugin indent on

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
"-- NeoBundle Configulation Section --
"=====================================
if !isdirectory(expand("~/.vim/bundle/neobundle.vim/"))
    finish
endif

if has('vim_starting')
    set runtimepath+=~/.vim/bundle/neobundle.vim/
endif
call neobundle#begin(expand('~/.vim/bundle/')) "required
NeoBundleFetch 'Shougo/neobundle.vim' " Let NeoBundle manage NeoBundle (Required)
call neobundle#end()

syntax on " なぜかこの辺に書かないと動かない

NeoBundle 'scrooloose/nerdtree'
let NERDTreeShowHidden = 1
command! Nt NERDTree

NeoBundle 'scrooloose/syntastic.git' " syntax checker
let g:syntastic_php_checkers = ['php'] " do not use phpmd and phpcs
let g:syntastic_javascript_checkers = ['jshint']
let g:syntastic_html_tidy_exec = 'tidy5'
let g:syntastic_eruby_ruby_quiet_messages =
    \ {'regex': 'possibly useless use of a variable in void context'}
let g:syntastic_html_tidy_ignore_errors=[
    \'proprietary attribute "ng-'
\]

NeoBundle 'kannokanno/previm' " preview markdown
let g:previm_open_cmd="open -a Safari"
augroup PrevimSettings
    autocmd!
    autocmd BufNewFile,BufRead *.{md,mdwn,mkd,mkdn,mark*} set filetype=markdown
augroup END

NeoBundle 'tpope/vim-fugitive' "git commands on vim
NeoBundle 'mhinz/vim-startify' " startpage of vim
NeoBundle 'terryma/vim-multiple-cursors'
NeoBundle 'tomtom/tcomment_vim'
NeoBundle 'mattn/emmet-vim'
NeoBundle 'wakatime/vim-wakatime'
NeoBundle 'Shougo/unite.vim'
NeoBundle 'airblade/vim-gitgutter'
NeoBundle 'editorconfig/editorconfig-vim'
NeoBundle 'hashivim/vim-terraform'
NeoBundle 'vim-scripts/phpfolding.vim'

NeoBundle 'thinca/vim-zenspace' " hightlight full-width space like this 　
let g:zenspace#default_mode = 'on'
augroup vimrc-highlight
    autocmd!
    autocmd ColorScheme * highlight ZenSpace ctermbg=Red guibg=Red
augroup END

NeoBundle 'nathanaelkane/vim-indent-guides'
let g:indent_guides_enable_on_vim_startup=1
let g:indent_guides_start_level=2
let g:indent_guides_color_change_percent =5
let g:indent_guides_guide_size = 1

NeoBundle 'glidenote/memolist.vim'
let g:memolist_path = expand("~/Documents/Memos")
let g:memolist_memo_suffix = "md"
let g:memolist_ex_cmd = 'NERDTree'

NeoBundle 'Shougo/neocomplete'
let g:neocomplete#enable_at_startup = 1

NeoBundle 'itchyny/lightline.vim'
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

call neobundle#end()

NeoBundleCheck

