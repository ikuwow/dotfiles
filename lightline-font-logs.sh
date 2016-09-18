#!/bin/bash

git clone git@github.com:Lokaltog/vim-powerline.git
cd vim-powerline/fontpatcher
fontforge -script ./fontpatcher /Library/Fonts/OsakaMono.ttf
cp OsakaMono-Powerline.ttf ~/Library/Fonts/
