vim.g.mapleader = ' '

vim.keymap.set('', '<C-n>', ':NERDTreeToggle<CR>')
vim.keymap.set('n', '<leader><space>', ':nohlsearch<CR>', {noremap = true})
vim.keymap.set('n', '<leader>s', ':set nolist!<CR>', {silent = true})
vim.keymap.set("v", "<C-c>", '"+y', { silent = true })
vim.keymap.set("i", "<C-v>", "<C-r>+", { silent = true })
vim.keymap.set("n", "<C-s>", ":write<cr>", { silent = true })
vim.keymap.set("n", "<C-q>", ":quit<cr>", { silent = true })
