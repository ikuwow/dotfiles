-- A claudecode.nvim terminal provider that holds several Claude Code sessions
-- in one panel on the right, one shown at a time. Each session is a terminal
-- buffer, and the panel is one window whose buffer changes to the shown
-- session, so switching sessions leaves the panel's size as it is and keeps
-- each session's scrollback.
--
-- Every session connects to this nvim's claudecode.nvim server: claudecode.nvim
-- builds the command and its environment, CLAUDE_CODE_SSE_PORT included, and
-- passes them to open(). The server sends selections and @ mentions to every
-- connected session, and claudecode.nvim's own commands (:ClaudeCode,
-- :ClaudeCodeFocus, a diff's window placement) act on the shown session.

local M = {}

local sessions = {} ---@type integer[] terminal buffers, oldest first
local active = nil ---@type integer?
local new_requested = false

local function valid(buf)
  return buf ~= nil and vim.api.nvim_buf_is_valid(buf)
end

local function index_of(buf)
  for i, b in ipairs(sessions) do
    if b == buf then
      return i
    end
  end
end

-- The window in the current tab that shows a session
local function panel_win()
  for _, win in ipairs(vim.api.nvim_tabpage_list_wins(0)) do
    if index_of(vim.api.nvim_win_get_buf(win)) then
      return win
    end
  end
end

local function enter(win, config)
  vim.api.nvim_set_current_win(win)
  if not config or config.auto_insert ~= false then
    vim.cmd.startinsert()
  end
end

-- Shows buf in the panel, opening the panel when the current tab has none.
-- Returns the panel window, with the cursor back in the window it was in.
local function show(buf, config)
  local win = panel_win()
  if not win then
    local from = vim.api.nvim_get_current_win()
    local side = config and config.split_side == "left" and "topleft " or "botright "
    local width = math.floor(vim.o.columns * ((config and config.split_width_percentage) or 0.4))
    vim.cmd(side .. width .. "vsplit")
    win = vim.api.nvim_get_current_win()
    vim.api.nvim_win_set_buf(win, buf)
    vim.wo[win].number = false
    vim.wo[win].relativenumber = false
    vim.wo[win].signcolumn = "no"
    if vim.api.nvim_win_is_valid(from) then
      vim.api.nvim_set_current_win(from)
    end
  else
    vim.api.nvim_win_set_buf(win, buf)
  end
  active = buf
  return win
end

local function hide()
  local win = panel_win()
  if win then
    -- The only window of the last tab cannot close (E444), so the panel stays
    -- there; the only window of another tab closes with its tab. The
    -- session's buffer stays hidden either way.
    pcall(vim.api.nvim_win_close, win, false)
  end
end

-- Drops buf from the sessions. keep leaves the buffer in place, so the output
-- of a session that failed stays readable with :buffer.
local function forget(buf, keep)
  local i = index_of(buf)
  if not i then
    return
  end
  -- Found while buf still counts as a session
  local win = panel_win()
  table.remove(sessions, i)
  if active == buf then
    active = sessions[math.min(i, #sessions)]
    if win and vim.api.nvim_win_get_buf(win) == buf then
      if active then
        vim.api.nvim_win_set_buf(win, active)
      else
        hide()
      end
    end
  end
  if valid(buf) and not keep then
    vim.api.nvim_buf_delete(buf, { force = true })
  end
end

local function spawn(cmd_string, env_table, config)
  local buf = vim.api.nvim_create_buf(false, false)
  vim.bo[buf].bufhidden = "hide"
  table.insert(sessions, buf)
  local win = show(buf, config)
  local ok, job
  vim.api.nvim_win_call(win, function()
    -- jobstart() raises E475 when the command is not executable
    ok, job = pcall(vim.fn.jobstart, require("claudecode.utils").parse_command(cmd_string), {
      term = true,
      env = env_table,
      cwd = config and config.cwd,
      on_exit = function(_, code)
        vim.schedule(function()
          -- 129 is the SIGHUP that jobstop(), deleting the buffer, and
          -- quitting nvim send
          local failed = code ~= 0 and code ~= 129
          if failed then
            vim.notify(
              ("Claude Code exited with code %d; its output stays in buffer %d"):format(code, buf),
              vim.log.levels.WARN
            )
          end
          forget(buf, failed)
          if failed and valid(buf) then
            -- Out of the filetype that edgy.nvim pulls into the Claude panel
            vim.bo[buf].filetype = ""
          end
        end)
      end,
    })
  end)
  if not ok or job <= 0 then
    forget(buf)
    vim.notify("Failed to start " .. cmd_string .. (ok and "" or (": " .. tostring(job))), vim.log.levels.ERROR)
    return
  end
  vim.bo[buf].filetype = "claudecode"
  require("claudecode.utils").map_terminal_suspend(buf)
  vim.api.nvim_create_autocmd("BufEnter", {
    buffer = buf,
    callback = function()
      -- A session that exited keeps its buffer for reading, and a key in
      -- Terminal mode would close it
      if index_of(buf) and (not config or config.auto_insert ~= false) then
        vim.cmd.startinsert()
      end
    end,
  })
  return win
end

-- claudecode.nvim's provider interface

function M.setup() end

function M.is_available()
  return true
end

function M.open(cmd_string, env_table, config, focus)
  local win
  if new_requested or not valid(active) then
    new_requested = false
    win = spawn(cmd_string, env_table, config)
  else
    win = show(active, config)
  end
  if win and focus ~= false then
    enter(win, config)
  end
end

function M.close()
  if not valid(active) then
    return
  end
  local job = vim.bo[active].channel
  if job > 0 then
    vim.fn.jobstop(job)
  end
end

function M.simple_toggle(cmd_string, env_table, config)
  if panel_win() then
    hide()
  else
    M.open(cmd_string, env_table, config, true)
  end
end

function M.focus_toggle(cmd_string, env_table, config)
  local win = panel_win()
  if not win then
    M.open(cmd_string, env_table, config, true)
  elseif win == vim.api.nvim_get_current_win() then
    hide()
  else
    enter(win, config)
  end
end

function M.toggle(cmd_string, env_table, config)
  M.simple_toggle(cmd_string, env_table, config)
end

function M.get_active_bufnr()
  if valid(active) then
    return active
  end
end

function M._get_terminal_for_test()
  return nil
end

-- Session commands

-- Starts another session in the panel. args are passed to claude, so
-- "--resume" picks a past conversation for it.
function M.new(args)
  new_requested = true
  require("claudecode.terminal").open({}, args)
end

-- Shows the session step places after the shown one, wrapping around
function M.cycle(step)
  if #sessions == 0 then
    return
  end
  local i = index_of(active) or 1
  local buf = sessions[(i - 1 + step) % #sessions + 1]
  local win = show(buf)
  if vim.api.nvim_get_current_win() == win then
    vim.cmd.startinsert()
  end
end

-- "2/3" for the second of three sessions, for the panel title
function M.label()
  local i = index_of(vim.api.nvim_get_current_buf()) or index_of(active)
  if not i then
    return ""
  end
  return i .. "/" .. #sessions
end

return M
