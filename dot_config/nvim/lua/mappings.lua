-- [[ Basic Keymaps ]]
-- Keymaps for better default experience
-- See `:help vim.keymap.set()`
vim.keymap.set({ 'n', 'v' }, '<Space>', '<Nop>', { silent = true })

-- Remap for dealing with word wrap
vim.keymap.set({ 'n', 'x' }, 'k', "v:count == 0 ? 'gk' : 'k'", { expr = true, silent = true })
vim.keymap.set({ 'n', 'x' }, 'j', "v:count == 0 ? 'gj' : 'j'", { expr = true, silent = true })
vim.keymap.set({ 'n', 'v' }, '<Up>', "v:count == 0 ? 'gk' : 'k'", { expr = true, silent = true })
vim.keymap.set({ 'n', 'v' }, '<Down>', "v:count == 0 ? 'gj' : 'j'", { expr = true, silent = true })

-- move selected lines up and down as a group in visual mode
vim.keymap.set("n", "<A-j>", ":m .+1<CR>==")
vim.keymap.set("v", "<A-j>", ":m '>+1<CR>gv=gv")
vim.keymap.set("i", "<A-j>", "<Esc>:m .+1<CR>==gi")
vim.keymap.set("n", "<A-k>", ":m .-2<CR>==")
vim.keymap.set("v", "<A-k>", ":m '<-2<CR>gv=gv")
vim.keymap.set("i", "<A-k>", "<Esc>:m .-2<CR>==gi")

-- Resize window using <shift> arrow keys
vim.keymap.set("n", "<S-Up>", "<cmd>resize +2<CR>")
vim.keymap.set("n", "<S-Down>", "<cmd>resize -2<CR>")
vim.keymap.set("n", "<S-Left>", "<cmd>vertical resize -2<CR>")
vim.keymap.set("n", "<S-Right>", "<cmd>vertical resize +2<CR>")

-- put the line below at the end of the current line without moving the cursor
vim.keymap.set("n", "J", "mzJ`z")

-- keep the cursor in the middle of the screen when scrolling up and down and through searches
vim.keymap.set("n", "<C-d>", "<C-d>zz")
vim.keymap.set("n", "<C-u>", "<C-u>zz")
vim.keymap.set("n", "n", "nzzzv")
vim.keymap.set("n", "N", "Nzzzv")

-- Better indent
vim.keymap.set("v", "<", "<gv")
vim.keymap.set("v", ">", ">gv")

-- paste/replace over the highlighted text without replacing the paste buffer
vim.keymap.set("x", "<leader>p", [["_dP]])
-- delete the selection without adding it to the paste buffer
vim.keymap.set({"n", "v"}, "<leader>d", [["_d]])

-- paste from the system clipboard
vim.keymap.set("i", "<C-v>", "<C-r>+")

-- command mode
vim.keymap.set("n", ";", ":", { nowait = true })

-- toggle showing blank caracters
vim.keymap.set("n", "<leader>s", ":set nolist!<CR>")

-- format the file
vim.keymap.set("n", "<leader>fm", vim.lsp.buf.format)

-- Indent the file
vim.keymap.set("n", "<leader>m", "mZgg=G'Z")

-- replace the word under the cursor
vim.keymap.set("n", "<leader>r", [[:%s/\<<C-r><C-w>\>/<C-r><C-w>/gI<Left><Left><Left>]])

-- make the current file executable
vim.keymap.set("n", "<leader>x", "<cmd>!chmod +x %<CR>", { silent = true })

-- Toggle undotree
vim.keymap.set("n", "<leader>u", vim.cmd.UndotreeToggle)

-- go to  beginning and end
vim.keymap.set("i", "<C-b>", "<ESC>^i")
vim.keymap.set("i", "<C-e>", "<End>")

-- navigate within insert mode
vim.keymap.set("i", "<C-h>", "<Left>")
vim.keymap.set("i", "<C-j>", "<Down>")
vim.keymap.set("i", "<C-k>", "<Up>")
vim.keymap.set("i", "<C-l>", "<Right>")

-- no highlight
vim.keymap.set("n", "<ESC>", "<cmd> noh <CR>")

-- switch between windows
vim.keymap.set("n", "<C-h>", "<C-w>h")
vim.keymap.set("n", "<C-j>", "<C-w>j")
vim.keymap.set("n", "<C-k>", "<C-w>k")
vim.keymap.set("n", "<C-l>", "<C-w>l")
vim.keymap.set("n", "<C-Left>", "<C-w>h")
vim.keymap.set("n", "<C-Down>", "<C-w>j")
vim.keymap.set("n", "<C-Up>", "<C-w>k")
vim.keymap.set("n", "<C-Right>", "<C-w>l")

-- save file
vim.keymap.set("n", "<C-s>", "<cmd> w <CR>")

-- copy whole file
vim.keymap.set("n", "<C-c>", "<cmd> %y+ <CR>")

-- copy the selection to the system clipboard
vim.keymap.set("v", "<C-c>", '"+y')

-- toggle line number
vim.keymap.set("n", "<leader>n", "<cmd> set nu! <CR>")
-- toggle relative number
vim.keymap.set("n", "<leader>rn", "<cmd> set rnu! <CR>")

-- new buffer
vim.keymap.set("n", "<leader>b", "<cmd> enew <CR>")

-- Quit all
vim.keymap.set("n", "<leader>qa", "<cmd> qall <CR>")

-- Close window
vim.keymap.set("n", "<leader>c", "<cmd> close <CR>")

-- Open split
vim.keymap.set("n", "<leader>sp", "<cmd> split <CR>")
vim.keymap.set("n", "<leader>vs", "<cmd> vsplit <CR>")
