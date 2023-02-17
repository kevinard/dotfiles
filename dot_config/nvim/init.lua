-- Install packer
local install_path = vim.fn.stdpath 'data' .. '/site/pack/packer/start/packer.nvim'
local is_bootstrap = false
if vim.fn.empty(vim.fn.glob(install_path)) > 0 then
  is_bootstrap = true
  vim.fn.system { 'git', 'clone', '--depth', '1', 'https://github.com/wbthomason/packer.nvim', install_path }
  vim.cmd [[packadd packer.nvim]]
end

require('packer').init {
  profile = {
    enable = true,
    threshold = 0, -- the amount in ms that a plugins load time must be over for it to be included in the profile
  },

  display = {
    open_fn = function()
      return require("packer.util").float { border = "rounded" }
    end,
  },
}

require('packer').startup(function(use)
  use 'lewis6991/impatient.nvim'

  -- Package manager
  use 'wbthomason/packer.nvim'

  use { -- LSP Configuration & Plugins
    'neovim/nvim-lspconfig',
    requires = {
      -- Automatically install LSPs to stdpath for neovim
      'williamboman/mason.nvim',
      'williamboman/mason-lspconfig.nvim',

      -- Useful status updates for LSP
      'j-hui/fidget.nvim',
    },
  }

  use { -- Autocompletion
    'hrsh7th/nvim-cmp',
    requires = { 'hrsh7th/cmp-nvim-lsp', 'L3MON4D3/LuaSnip', 'saadparwaiz1/cmp_luasnip', 'hrsh7th/cmp-buffer', 'hrsh7th/cmp-path', 'hrsh7th/cmp-cmdline', 'ray-x/cmp-treesitter' },
  }

  use { -- Highlight, edit, and navigate code
    'nvim-treesitter/nvim-treesitter',
    run = function()
      pcall(require('nvim-treesitter.install').update { with_sync = true })
    end,
  }

  use { -- Additional text objects via treesitter
    'nvim-treesitter/nvim-treesitter-textobjects',
    after = 'nvim-treesitter',
  }

  -- Git related plugins
  use 'tpope/vim-fugitive'
  use 'lewis6991/gitsigns.nvim'
  use { 'sindrets/diffview.nvim', requires = 'nvim-lua/plenary.nvim' }

  use { -- Add/change/delete surrounding delimiter pairs with ease
    'kylechui/nvim-surround',
    tag = "*", -- Use for stability; omit to use `main` branch for the latest features
  }

  use 'RRethy/vim-illuminate' -- Highlight other uses of the word under the cursor

  use 'windwp/nvim-autopairs'
  use 'RRethy/nvim-treesitter-endwise'

  use 'ThePrimeagen/refactoring.nvim'

  use 'Shatur/neovim-session-manager'

  use { -- Terminal
    'akinsho/toggleterm.nvim',
    tag = '*',
  }

  use 'stevearc/dressing.nvim'
  use { 'catppuccin/nvim', as = 'catppuccin' } -- Catppuccin Theme
  use 'nvim-tree/nvim-web-devicons'
  use { 'romgrk/barbar.nvim', wants = 'nvim-web-devicons' } -- Buffer/tab bar
  use 'nvim-lualine/lualine.nvim' -- Fancier statusline
  use 'nvim-tree/nvim-tree.lua' -- Tree
  use 'lukas-reineke/indent-blankline.nvim' -- Add indentation guides even on blank lines
  use 'numToStr/Comment.nvim' -- "gc" to comment visual regions/lines
  use 'mbbill/undotree'

  -- Fuzzy Finder (files, lsp, etc)
  use { 'nvim-telescope/telescope.nvim', branch = '0.1.x', requires = { 'nvim-lua/plenary.nvim' } }

  use 'ray-x/go.nvim'
  use "alker0/chezmoi.vim"

  if is_bootstrap then
    require('packer').sync()
  end
end)

-- When we are bootstrapping a configuration, it doesn't
-- make sense to execute the rest of the init.lua.
--
-- You'll need to restart nvim, and then it will work.
if is_bootstrap then
  print '=================================='
  print '    Plugins are being installed'
  print '    Wait until Packer completes,'
  print '       then restart nvim'
  print '=================================='
  return
end

require('impatient')

-- Set <space> as the leader key
-- See `:help mapleader`
--  NOTE: Must happen before plugins are required (otherwise wrong leader will be used)
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

require("settings")
require("colorscheme")
require("mappings")

-- Automatically source and re-compile packer whenever you save this init.lua
local packer_group = vim.api.nvim_create_augroup('Packer', { clear = true })
vim.api.nvim_create_autocmd('BufWritePost', {
  command = 'source <afile> | silent! LspStop | silent! LspStart | PackerCompile',
  group = packer_group,
  pattern = vim.fn.expand '$MYVIMRC',
})

-- [[ Highlight on yank ]]
-- See `:help vim.highlight.on_yank()`
local highlight_group = vim.api.nvim_create_augroup('YankHighlight', { clear = true })
vim.api.nvim_create_autocmd('TextYankPost', {
  callback = function()
    vim.highlight.on_yank()
  end,
  group = highlight_group,
  pattern = '*',
})

-- Remove trailing spaces before saving file
local trailingspaces_group = vim.api.nvim_create_augroup('TrailingSpaces', {})
vim.api.nvim_create_autocmd({"BufWritePre"}, {
  group = trailingspaces_group,
  pattern = "*",
  command = [[%s/\s\+$//e]],
})

