-- Set lualine as statusline
-- See `:help lualine.txt`
require('lualine').setup {
  options = {
    icons_enabled = true,
    theme = 'catppuccin',
    component_separators = { left = '', right = ''},
    section_separators = { left = '', right = ''},
    disabled_filetypes = {
      statusline = {},
      winbar = {},
    },
    ignore_focus = {},
    always_divide_middle = true,
    globalstatus = true,
  },
  sections = {
    lualine_a = {'mode'},
    lualine_b = {{'b:gitsigns_head', icon = ''},
      {
        'diagnostics',
        -- Table of diagnostic sources, available sources are:
        --   'nvim_lsp', 'nvim_diagnostic', 'nvim_workspace_diagnostic', 'coc', 'ale', 'vim_lsp'.
        -- or a function that returns a table as such:
        --   { error=error_cnt, warn=warn_cnt, info=info_cnt, hint=hint_cnt }
        sources = { 'nvim_diagnostic', 'nvim_lsp' },

        -- Displays diagnostics for the defined severity types
        sections = { 'error', 'warn', 'info', 'hint' },

        diagnostics_color = {
          -- Same values as the general color option can be used here.
          error = 'DiagnosticError', -- Changes diagnostics' error color.
          warn  = 'DiagnosticWarn',  -- Changes diagnostics' warn color.
          info  = 'DiagnosticInfo',  -- Changes diagnostics' info color.
          hint  = 'DiagnosticHint',  -- Changes diagnostics' hint color.
        },
        -- symbols = {error = '', warn = '', info = '', hint = ''},
      }
    },
    lualine_c = {{'filename', path = 1}, 'searchcount'},
    lualine_x = {'encoding', 'filetype'},
    lualine_y = {'progress'},
    lualine_z = {'location'}
  },
  inactive_sections = {
    lualine_a = {},
    lualine_b = {},
    lualine_c = {'filename'},
    lualine_x = {'location'},
    lualine_y = {},
    lualine_z = {}
  },
  extensions = {
    'toggleterm',
    'nvim-tree',
  },
}

-- require("feline").setup({
--     components = require('catppuccin.groups.integrations.feline').get(),
-- })
--
-- vim.api.nvim_create_autocmd("ColorScheme", {
--   pattern = "*",
--   callback = function()
--       package.loaded["feline"] = nil
--       package.loaded["catppuccin.groups.integrations.feline"] = nil
--       require("feline").setup {
--           components = require("catppuccin.groups.integrations.feline").get(),
--       }
--   end,
-- })
