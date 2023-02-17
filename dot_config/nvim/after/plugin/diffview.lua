require("diffview").setup {
  enhanced_diff_hl = true,
  view = {
    merge_tool = {
      layout = "diff3_mixed",
    },
  },
  hooks = {
    diff_buf_read = function(bufnr)
      -- Change local options in diff buffers
      vim.opt_local.wrap = false
      vim.opt_local.list = false
      vim.opt_local.colorcolumn = { 80 }
    end,
  }
}

vim.keymap.set("n", "<leader>gd", "<cmd> DiffviewOpen <CR>")
vim.keymap.set("n", "<leader>gc", "<cmd> DiffviewClose <CR>")
vim.keymap.set("n", "<leader>gh", "<cmd> DiffviewFileHistory % <CR>")
