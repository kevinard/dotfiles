require('illuminate').configure({
  -- providers: provider used to get references in the buffer, ordered by priority
  providers = {
    'lsp',
    'treesitter',
    'regex',
  },
  -- delay: delay in milliseconds
  delay = 120,
  -- filetypes_denylist: filetypes to not illuminate, this overrides filetypes_allowlist
  filetypes_denylist = {
    "dirvish",
    "fugitive",
    "help",
    "terminal",
    "packer",
    "lspinfo",
    "TelescopePrompt",
    "TelescopeResults",
    "mason",
    "checkhealth",
    "man",
    "toggleterm",
    "NvimTree",
    "DressingSelect",
  },
  -- under_cursor: whether or not to illuminate under the cursor
  under_cursor = true,
  -- min_count_to_highlight: minimum number of matches required to perform highlighting
  min_count_to_highlight = 2,
})

vim.keymap.set("n", "<leader>i", "<cmd> IlluminateToggle <CR>")
