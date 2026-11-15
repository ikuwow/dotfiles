-- An nvim started without file arguments, as bin/nvim-ide starts it, opens
-- with the file tree on the left and Claude Code on the right, and the cursor
-- in the editor area

local function open()
  if vim.fn.argc() > 0 then
    return
  end
  local editor = vim.api.nvim_get_current_win()
  vim.cmd("Fern . -drawer -stay")
  vim.cmd("ClaudeCodeOpen")
  vim.schedule(function()
    vim.cmd.stopinsert()
    if vim.api.nvim_win_is_valid(editor) then
      vim.api.nvim_set_current_win(editor)
    end
  end)
end

-- fern.vim fills its buffer from a BufReadCmd autocmd, which an autocmd
-- triggers only when nested.
-- On the first run, the main config installs the missing plugins and
-- sources this config from inside its VimEnter autocmd, too late for a
-- VimEnter handler to fire and not nested, so the layout opens once that
-- autocmd is done. A later re-source ($MYVIMRC on save, :Sv) also lands
-- here, where an existing session means the layout is already open.
if vim.v.vim_did_enter == 1 then
  if not require("ide.claude").get_active_bufnr() then
    vim.schedule(open)
  end
else
  vim.api.nvim_create_autocmd("VimEnter", {
    group = vim.api.nvim_create_augroup("ide-startup", { clear = true }),
    nested = true,
    callback = open,
  })
end
