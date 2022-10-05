local M = {}

M.treesitter = {
  ensure_installed = {
    "vim",
    "lua",
    "html",
    "css",
    "typescript",
    "c",
    "bash",
    "c_sharp",
    "dockerfile",
    "elixir",
    "gitignore",
    "go",
    "javascript",
    "json",
    "ledger",
    "markdown",
    "php",
    "python",
    "ruby",
    "rust",
    "scss",
    "sql",
    "yaml",
  },
}

M.mason = {
  ensure_installed = {
    "lua-language-server",
    "bash-language-server",
    "marksman",
  },
}

-- git support in nvimtree
M.nvimtree = {
  git = {
    enable = true,
  },

  renderer = {
    highlight_git = true,
    icons = {
      show = {
        git = true,
      },
    },
  },
}

return M
