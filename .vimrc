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

"全てのfiletype系設定を解除
filetype off

"NeoBUndle"
if has('vim_starting')
  set runtimepath+=~/.vim/bundle/neobundle/
endif
  call neobundle#rc(expand('~/.vim/bundle/'))

"ここに書いたものが:NeoBundleInstallでインストールされる
"NeoBundle 'Shougo/neobundle.vim'
"NeoBundle 'Shougo/vimproc'
NeoBundle 'scrooloose/nerdtree'
let NERDTreeShowHidden = 1
"NeoBundle 'altercation/vim-colors-solarized'
"NeoBundle 'croaker/mustang-vim'
"NeoBundle 'jeffreyiacono/vim-colors-wombat'
"NeoBundle 'Shougo/unite.vim'
"NeoBundle 'ujihisa/unite-colorscheme'
"NeoBundle 'nanotech/jellybeans.vim'
"NeoBundle 'vim-scripts/Lucius'
"NeoBundle 'vim-scripts/Zenburn'
"NeoBundle 'mrkn/mrkn256.vim'
"NeoBundle 'jpo/vim-railscasts-theme'
"NeoBundle 'therubymug/vim-pyte'
"NeoBundle 'tomasr/molokai'
NeoBundle 'tpope/vim-fugitive'

" vim-over
" :OverCommandLineで起動、%s/old/new/gでハイライトされる
" NeoBundle 'osyo-manga/vim-over'

"先ほど解除したのを復帰
"後者は'filetype on'も適用される
filetype plugin on
filetype indent on
autocmd FileType * setlocal formatoptions-=ro


"NeoBundleFetch 'Shougo/neobundle.vim'

"NeoBundle 'Shougo/vimproc', {
"      \ 'build' : {
"      \     'windows' : 'make -f make_mingw32.mak',
"      \     'cygwin' : 'make -f make_cygwin.mak',
"      \     'mac' : 'make -f make_mac.mak',
"      \     'unix' : 'make -f make_unix.mak',
"      \    },
"      \ }
"
NeoBundleCheck
""""""""""""""

"ファイラー。ちょっとうっとうしいから
"必要なときにコマンドうつわ。
"autocmd VimEnter * NERDTree " launch NERDTree automatically at opening files
command Nt NERDTree

"文法チェック
nmap ,l :call PHPLint()

function PHPLint()
    let result = system( &ft . ' -l ' . bufname(""))
    echo result
endfunction

" MATLAB関係
source ~/.vim/matlab/syntax/matlab.vim
source ~/.vim/matlab/indent/matlab.vim
source ~/.vim/matlab/ftplugin/matlab.vim
