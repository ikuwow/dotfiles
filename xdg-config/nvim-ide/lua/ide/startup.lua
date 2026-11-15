-- An nvim started without file arguments, as bin/nvim-ide starts it, opens
-- with the file tree on the left and Claude Code on the right, and the cursor
-- in the editor area
vim.api.nvim_create_autocmd("VimEnter", {
  group = vim.api.nvim_create_augroup("ide-startup", { clear = true }),
  callback = function()
    if vim.fn.argc() > 0 then
      return
    end
    local editor = vim.api.nvim_get_current_win()
    vim.cmd("Neotree show")
    vim.cmd("ClaudeCodeOpen")
    vim.schedule(function()
      vim.cmd.stopinsert()
      if vim.api.nvim_win_is_valid(editor) then
        vim.api.nvim_set_current_win(editor)
      end
    end)
  end,
})
