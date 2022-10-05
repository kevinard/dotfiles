local HOME = os.getenv("HOME")
local indent = 2
local backupdir = HOME .. "/.vim-tmp," .. HOME .. "/.tmp," .. HOME .. "/tmp,/var/tmp,/tmp"

vim.opt.updatetime = 250
vim.opt.showmode = false
vim.opt.hidden = true
vim.opt.shortmess = vim.opt.shortmess + "c"
vim.opt.signcolumn = "yes"
vim.opt.number = true
vim.opt.showcmd = true
vim.opt.cursorline = true
vim.opt.lazyredraw = true
vim.opt.showmatch = true
vim.opt.incsearch = true
vim.opt.hlsearch = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.backup = true
vim.opt.backupdir = backupdir
vim.opt.backupskip = "/tmp/*,/private/tmp/*"
vim.opt.directory = backupdir
vim.opt.writebackup = true
vim.opt.backspace = "indent,eol,start"
vim.opt.autoread = true
vim.opt.autoindent = true
vim.opt.smartindent = true
vim.opt.smarttab = true
vim.opt.shiftwidth = indent
vim.opt.tabstop = indent
vim.opt.softtabstop = indent
vim.opt.expandtab = true
vim.opt.listchars = "tab:>-,trail:·,eol:¬"
vim.opt.title = true
vim.opt.ruler = true
vim.opt.clipboard = vim.opt.clipboard + "unnamedplus"
vim.opt.path = vim.opt.path + "**"

vim.cmd('colorscheme nord')
vim.cmd('syntax enable')
vim.cmd('filetype on')
vim.cmd('filetype indent on')
vim.cmd('filetype plugin on')

vim.g.nord_cursor_line_number_background = 1
vim.g.nord_italic = 1
vim.g.nord_underline = 1

vim.g.lightline = {
  colorscheme = 'nord',
  active = {
    left = { { 'mode', 'paste' }, 
             { 'gitbranch', 'readonly', 'filename', 'modified' } }
  },
  component_function = {
    gitbranch = 'fugitive#head'
  },
}
