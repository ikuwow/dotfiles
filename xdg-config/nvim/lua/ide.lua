-- Opens a file for `ide --open`, which calls open() through the RPC socket of
-- the nvim that ide starts
local M = {}

-- The first window of the current tab that shows a file buffer; the tree,
-- terminals, help, and floating windows have a buftype or a relative
-- position and are passed over
local function editor_window()
  for _, win in ipairs(vim.api.nvim_tabpage_list_wins(0)) do
    local buf = vim.api.nvim_win_get_buf(win)
    if vim.api.nvim_win_get_config(win).relative == '' and vim.bo[buf].buftype == '' then
      return win
    end
  end
end

-- A line of 0 leaves the cursor where the file last had it
function M.open(path, line)
  local win = editor_window()
  if win then
    vim.api.nvim_set_current_win(win)
  else
    vim.cmd('botright vnew')
    -- A new window evens out the widths, so the tree goes back to its
    -- configured width
    local ok, tree = pcall(require, 'nvim-tree.api')
    if ok then
      tree.tree.resize()
    end
  end
  -- Leaves visual, insert, or command-line mode, so the file is shown in
  -- normal mode whatever the user was doing
  vim.api.nvim_feedkeys(vim.api.nvim_replace_termcodes('<C-\\><C-N>', true, false, true), 'n', false)
  vim.cmd.edit(vim.fn.fnameescape(path))
  if line > 0 then
    line = math.min(line, vim.api.nvim_buf_line_count(0))
    vim.api.nvim_win_set_cursor(0, { line, 0 })
    vim.cmd('normal! zz')
  end
  return 'Opened ' .. path
end

return M
