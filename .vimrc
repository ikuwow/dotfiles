" vimtutorというコマンドの存在を忘れるな。
" ちゃんとそのうちやるんだぞ。
" がんばれよ

" Basic Configuration 
set nu
set title " display filename (not Thank you for using Vim.)
syntax on
set nocompatible " do not use vi compatible mode
set nobackup "チルダつきのファイルが邪魔
set ic "検索時に大文字小文字を区別しない
set noundofile ".un~ファイルを作らない
set ruler " display ruler (60,7 13%)
set hlsearch " highlight the search word
set showcmd " show inputting key

    
"tab関係
set shiftwidth=4
"softtabstop is equal to tabstop in defalut
"set softtabstop=4
set autoindent
set expandtab "convert tab to spaces
set tabstop=4 " spaces number of tab

" ファイルごとにtab幅を変える。
" 動かない、詳細を確認すべし
" augroup vimrc
" autocmd! FileType html setlocal shiftwidth=2 tabstop=2 softtabstop=2
" augroup END

" 全角スペースの表示
highlight ZenkakuSpace ctermbg=red guibg=#ff0000
au BufWinEnter * let w:m3 = matchadd("ZenkakuSpace", '　')
" au WinEnter * let w:m3 = matchadd("ZenkakuSpace", '　')

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

" MATLAB関係
source ~/.vim/matlab/syntax/matlab.vim
source ~/.vim/matlab/indent/matlab.vim
source ~/.vim/matlab/ftplugin/matlab.vim

"=============================================
"  NeoBundle Configulation Section (2014/7/12)
"=============================================

if has('vim_starting') " at launching vim only
    set runtimepath+=~/.vim/bundle/neobundle.vim/
endif

call neobundle#rc(expand('~/.vim/bundle/')) "required

NeoBundleFetch 'Shougo/neobundle.vim' " Let NeoBundle manage NeoBundle (Required)

" ~ My Bundles Here... ~
NeoBundle 'scrooloose/nerdtree' " Filer plugin
let NERDTreeShowHidden = 1 " Display hidden files and folders on NERDTree
NeoBundle 'tpope/vim-fugitive' "git commands on vim
NeoBundle 'scrooloose/syntastic.git' " syntax checker

call neobundle#end()
filetype plugin indent on


" If there are uninstalled bundles found on startup,
" this will conveniently prompt you to install them.
NeoBundleCheck


" NeoBundle Configulation End 
"========================================


" launch NERDTree automatically at opening files
" autocmd VimEnter * NERDTree 

" alias of NERDTree
command! Nt NERDTree

" don't automatically continue comment line
autocmd FileType * setlocal formatoptions-=ro

