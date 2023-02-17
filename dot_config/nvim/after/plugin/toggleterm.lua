-- Terminal
require("toggleterm").setup {
    open_mapping = [[<A-'>]],
    shade_terminals = false,
    autochdir = true,
    insert_mappings = true,
    terminal_mappings = true,
}

vim.keymap.set('n', "<A-i>", "<cmd>ToggleTerm direction=float<cr>", { desc = "ToggleTerm float" })
vim.keymap.set('n', "<A-h>", "<cmd>ToggleTerm size=10 direction=horizontal<cr>", { desc = "ToggleTerm horizontal split" })
vim.keymap.set('n', "<A-v>", "<cmd>ToggleTerm size=80 direction=vertical<cr>", { desc = "ToggleTerm vertical split" })
vim.keymap.set({'n', 't', 'i'}, "<F7>", "<cmd>ToggleTermToggleAll<cr>", { desc = "Toggle terminal" })

-- escape terminal mode
vim.keymap.set("t", "<esc>", vim.api.nvim_replace_termcodes("<C-\\><C-N>", true, true, true))

-- navigate within terminal mode
vim.keymap.set('t', '<C-h>', [[<Cmd>wincmd h<CR>]])
vim.keymap.set('t', '<C-j>', [[<Cmd>wincmd j<CR>]])
vim.keymap.set('t', '<C-k>', [[<Cmd>wincmd k<CR>]])
vim.keymap.set('t', '<C-l>', [[<Cmd>wincmd l<CR>]])
vim.keymap.set('t', '<C-Left>', [[<Cmd>wincmd h<CR>]])
vim.keymap.set('t', '<C-Down>', [[<Cmd>wincmd j<CR>]])
vim.keymap.set('t', '<C-Up>', [[<Cmd>wincmd k<CR>]])
vim.keymap.set('t', '<C-Right>', [[<Cmd>wincmd l<CR>]])
