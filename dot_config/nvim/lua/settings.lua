-- [[ Setting options ]]
-- See `:help vim.o`
-- disable some builtin vim plugins
local default_plugins = {
  "2html_plugin",
  "getscript",
  "getscriptPlugin",
  "gzip",
  "logipat",
  "netrw",
  "netrwPlugin",
  "netrwSettings",
  "netrwFileHandlers",
  "matchit",
  "tar",
  "tarPlugin",
  "rrhelper",
  "spellfile_plugin",
  "vimball",
  "vimballPlugin",
  "zip",
  "zipPlugin",
  "tutor",
  "rplugin",
  "syntax",
  "synmenu",
  "optwin",
  "compiler",
  "bugreport",
  "ftplugin",
}

for _, plugin in pairs(default_plugins) do
  vim.g["loaded_" .. plugin] = 1
end

local default_providers = {
  "node",
  "perl",
  "python3",
  "ruby",
}

for _, provider in ipairs(default_providers) do
  vim.g["loaded_" .. provider .. "_provider"] = 0
end

-- Make line numbers default
vim.wo.number = true
vim.opt.numberwidth = 2

-- Enable mouse mode
vim.o.mouse = 'a'

-- Case insensitive searching UNLESS /C or capital in search
vim.o.ignorecase = true
vim.o.smartcase = true
vim.opt.incsearch = true
vim.o.hlsearch = true

-- Decrease update time
vim.o.updatetime = 250
vim.wo.signcolumn = 'yes'

-- disable swapfiles and save undo history instead
vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.undofile = true
-- vim.opt.undodir = os.getenv("HOME") .. "/.vim/undodir"

vim.opt.laststatus = 3 -- global statusline
vim.opt.showmode = false

vim.opt.title = true
vim.opt.clipboard = "unnamedplus"
vim.opt.cursorline = true

-- Indenting
vim.opt.expandtab = true
vim.opt.smarttab = true
vim.opt.shiftwidth = 2
vim.opt.smartindent = true
vim.o.breakindent = true
vim.opt.tabstop = 2
vim.opt.softtabstop = 2
vim.opt.autoindent = false

vim.opt.fillchars = { eob = " ", diff = "╱" }
vim.opt.listchars:append "tab:>-,trail:·,eol:¬,nbsp:⋅,space:⋅"

-- disable nvim intro
vim.opt.shortmess:append "sI"

vim.opt.splitbelow = true
vim.opt.splitright = true
vim.opt.termguicolors = true
vim.opt.timeoutlen = 400

-- go to previous/next line with h,l,left arrow and right arrow
-- when cursor reaches end/beginning of line
vim.opt.whichwrap:append "<>[]hl"

-- Set completeopt to have a better completion experience
vim.o.completeopt = 'menuone,noselect'
