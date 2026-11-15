local M = {}

-- Environment for the programs started in this nvim's terminals. A child
-- inherits NVIM_APPNAME=nvim-ide, so an nvim it starts, such as git's editor
-- or Claude Code's external editor, would load this config too; an empty
-- value makes that nvim use the default config. NVIM_APPNAME stays set in
-- this nvim itself, since stdpath() reads it on every call.
function M.child()
  return { NVIM_APPNAME = "" }
end

return M
