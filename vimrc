" vimtutorというコマンドの存在を忘れるな。
" ちゃんとそのうちやるんだぞ。
" がんばれよ

" Basic Configuration
set nu
set title " display filename (not Thank you for using Vim.)
syntax on
set nocompatible " do not use vi compatible mode
set nobackup "チルダつきのファイルが邪魔
set ic " ignore case, 検索時に大文字小文字を区別しない
if version >= 703
    set noundofile " .un~ファイルを作らない
endif
set ruler " display ruler (60,7 13%)
set hlsearch " highlight the search word
set showcmd " show inputting key
" set mouse=a " enable mouse control (select, scroll etc.)
set clipboard=unnamed " sharing clipboard
"set linebreak "auto linebreak

"tab関係
set shiftwidth=4
"softtabstop is equal to tabstop in defalut
"set softtabstop=4
set autoindent
set expandtab "convert tab to spaces
set tabstop=4 " spaces number of tab
set breakindent

" ファイルごとにtab幅を変える。
" 動かない、詳細を確認すべし
" augroup vimrc
" autocmd! FileType html setlocal shiftwidth=2 tabstop=2 softtabstop=2
" augroup END

" 全角スペースの表示
highlight ZenkakuSpace ctermbg=red guibg=#ff0000
au BufWinEnter * let w:m3 = matchadd("ZenkakuSpace", '　')
augroup HighlightTrailingSpaces
  autocmd!
  autocmd VimEnter,WinEnter,ColorScheme * highlight TrailingSpaces term=underline guibg=green ctermbg=green
autocmd VimEnter,WinEnter * match TrailingSpaces /\s\+$/
augroup END

"勝手に改行しないでね
set tw=0
set formatoptions=q
"t:本文を整形、c:コメントを整形
"o:'o','O'の時にコメント開始文字列を自動で挿入
"r:挿入モードでenterを打ち込むとコメント開始文字を自動で挿入

"文法チェック
nmap ,l :call PHPLint()

function! PHPLint() " exclamation mark means overriding the definition of function
    let result = system( &ft . ' -l ' . bufname(""))
    echo result
endfunction

" complement { after Enter
inoremap {<Enter> {}<Left><CR><ESC><S-o>

" don't automatically continue comment line
autocmd FileType * setlocal formatoptions-=ro

"=============================================
"  NeoBundle Configulation Section (2014/7/12)
"=============================================
if !isdirectory(expand("~/.vim/bundle/neobundle.vim/"))
    finish
endif
" if neobundle exists:

if has('vim_starting') " at launching vim only
    set runtimepath+=~/.vim/bundle/neobundle.vim/
endif

call neobundle#begin(expand('~/.vim/bundle/')) "required
NeoBundleFetch 'Shougo/neobundle.vim' " Let NeoBundle manage NeoBundle (Required)
call neobundle#end()

" ~ My Bundles Here... ~
NeoBundle 'scrooloose/nerdtree' " Filer plugin
NeoBundle 'tpope/vim-fugitive' "git commands on vim
NeoBundle 'scrooloose/syntastic.git' " syntax checker
NeoBundle 'toyamarinyon/vim-swift' " swift support
NeoBundle 'tyru/open-browser.vim'
NeoBundle 'kannokanno/previm' " preview markdown
NeoBundle 'thinca/vim-quickrun' " enable trying
NeoBundle 'mhinz/vim-startify' " startpage of vim
NeoBundle 'terryma/vim-multiple-cursors'
NeoBundle 'tomtom/tcomment_vim'
NeoBundle 'kchmck/vim-coffee-script'
NeoBundle 'mattn/emmet-vim'
NeoBundle 'wakatime/vim-wakatime'
NeoBundle 'Shougo/unite.vim'

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
    \     'readonly': '%{&readonly?"⭤":""}'
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

function! CurrentBranch()
    try
        if &ft !~? 'nerdtree' && exists('*fugitive#head') && strlen(fugitive#head())
            return "\u2B60 " . fugitive#head()
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
filetype plugin indent on

" phpmdやphpcsはキツすぎるので使わない
let g:syntastic_php_checkers = ['php']
let g:syntastic_eruby_ruby_quiet_messages =
    \ {'regex': 'possibly useless use of a variable in void context'}
let g:syntastic_html_tidy_ignore_errors=[
    \'proprietary attribute "ng-'
\]
let g:syntastic_javascript_checkers = ['jshint']
let g:syntastic_html_tidy_exec = 'tidy5'
" let g:syntastic_javascript_jshint_args = [ expand('~/.jshintrc') ]

" If there are uninstalled bundles found on startup,
" this will conveniently prompt you to install them.
NeoBundleCheck

" configuration for each plugin
let NERDTreeShowHidden = 1 " Display hidden files and folders on NERDTree
" let g:startify_custom_header = "Done is better than perfect." " startify custom header
" .mdファイルをmarkdownとして認識させる
augroup PrevimSettings
    autocmd!
    autocmd BufNewFile,BufRead *.{md,mdwn,mkd,mkdn,mark*} set filetype=markdown
augroup END

" launch NERDTree automatically at opening files
" autocmd VimEnter * NERDTree

" alias for each plugin
command! Nt NERDTree

" NeoBundle Configulation End
"========================================
