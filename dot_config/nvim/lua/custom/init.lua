local HOME = os.getenv("HOME")
local indent = 2
local backupdir = HOME .. "/.vim-tmp," .. HOME .. "/.tmp," .. HOME .. "/tmp,/var/tmp,/tmp"

vim.opt.updatetime = 250
vim.opt.showmode = false
vim.opt.hidden = true
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
vim.opt.listchars = "tab:>-,trail:·,eol:¬,nbsp:⋅"
vim.opt.title = true
vim.opt.ruler = true
vim.opt.clipboard = "unnamedplus"

vim.g.mapleader = " "
