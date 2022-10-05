local M = {}

-- add this table only when you want to disable default keys
M.disabled = {
}

M.general = {
  n = {
     [";"] = { ":", "command mode", opts = { nowait = true } },
     ["<leader>s"] = { ":set nolist!<CR>", "toggle showing blank caracters" },
  },
  v = {
     ["<C-c>"] = { '"+y', "copy selected text to clipboard" },
  },
  i = {
     ["<C-v>"] = { "<C-r>+", "paste text from clipboard" },
  },
}

-- more keybinds!

return M
