" MacVimの設定
set lines=60
set columns=120
set visualbell

" color schemes
syntax enable
colorscheme desert
set background=dark


highlight ZenkakuSpace ctermbg=red guibg=#ff0000
au WinEnter * let w:m3 = matchadd("ZenkakuSpace", '　')



