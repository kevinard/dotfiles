-- Enable `lukas-reineke/indent-blankline.nvim`
-- See `:help indent_blankline.txt`
require('indent_blankline').setup {
  char = "▏",
  context_char = "▏",
  use_treesitter = true,
  -- use_treesitter_scope = true,
  max_indent_increase = 1,
  space_char_blankline = " ",
  show_end_of_line = true,
  filetype_exclude = {
    "help",
    "terminal",
    "packer",
    "lspinfo",
    "TelescopePrompt",
    "TelescopeResults",
    "mason",
    "checkhealth",
    "man",
    "",
  },
  buftype_exclude = { "terminal" },
  show_trailing_blankline_indent = false,
  show_first_indent_level = true,
  show_current_context = true,
  show_current_context_start = false,
  context_highlight_list = {
    "IndentBlanklineIndent6",
  },
}

-- Toggle indent lines
vim.keymap.set("n", "<leader>sl", "<cmd> IndentBlanklineToggle <CR>")

-- Jump to current_context
vim.keymap.set("n", "<leader>cc", function()
  local ok, start = require("indent_blankline.utils").get_current_context(
    vim.g.indent_blankline_context_patterns,
    vim.g.indent_blankline_use_treesitter_scope
  )

  if ok then
    vim.api.nvim_win_set_cursor(vim.api.nvim_get_current_win(), { start, 0 })
    vim.cmd [[normal! _]]
  end
end, { desc = "Jump to current_context" })
