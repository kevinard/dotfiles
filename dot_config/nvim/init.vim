call plug#begin('~/.local/share/nvim/plugged')
Plug 'arcticicestudio/nord-vim'
Plug 'itchyny/lightline.vim'
Plug 'scrooloose/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
" Plug 'tpope/vim-fugitive'
Plug 'mhinz/vim-signify'
Plug 'tpope/vim-endwise'
Plug 'ledger/vim-ledger'
" Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
call plug#end()

let g:nord_cursor_line_number_background = 1
let g:nord_italic = 1
let g:nord_underline = 1

colorscheme nord

set updatetime=100
set noshowmode

let g:lightline = {
      \ 'colorscheme': 'nord',
      \ 'active': {
      \   'left': [ [ 'mode', 'paste' ],
      \             [ 'gitbranch', 'readonly', 'filename', 'modified' ] ]
      \ },
      \ 'component_function': {
      \   'gitbranch': 'fugitive#head'
      \ },
      \ }

map <C-n> :NERDTreeToggle<CR>
autocmd BufEnter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

" if hidden is not set, TextEdit might fail.
set hidden

" Better display for messages
"set cmdheight=2

" don't give |ins-completion-menu| messages.
set shortmess+=c

" always show signcolumns
set signcolumn=yes

set path+=**
syntax enable
set number
set showcmd
set cursorline
filetype on
filetype indent on
filetype plugin on
set lazyredraw
set showmatch
set incsearch
set hlsearch
set ignorecase
set smartcase
nnoremap <leader><space> :nohlsearch<CR>

set backup
set backupdir=~/.vim-tmp,~/.tmp,~/tmp,/var/tmp,/tmp
set backupskip=/tmp/*,/private/tmp/*
set directory=~/.vim-tmp,~/.tmp,~/tmp,/var/tmp,/tmp
set writebackup

set backspace=indent,eol,start  "Allow backspace in insert mode
set autoread

set autoindent
set smartindent
set smarttab
set shiftwidth=2
set tabstop=2 " number of visual spaces per TAB
set softtabstop=2 " number of spaces in tab when editing
set expandtab " tabs are spaces

" Display tabs and trailing spaces visually
set listchars=tab:>-,trail:·,eol:¬
nmap <silent> <leader>s :set nolist!<CR>

set title
set ruler

let g:deoplete#enable_at_startup = 1

set clipboard+=unnamedplus
