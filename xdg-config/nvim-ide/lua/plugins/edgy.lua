-- Fixed panels around the editor area: the file tree on the left, Claude Code
-- on the right, and shell terminals at the bottom. A split or a help window
-- opened in the editor area leaves the panels where they are.

local function snacks_at(pos)
  return function(_, win)
    local w = vim.w[win].snacks_win
    return w ~= nil and w.position == pos and w.relative == "editor"
  end
end

return {
  "folke/edgy.nvim",
  -- Loaded at startup, so the panels that startup opens are already placed
  lazy = false,
  opts = {
    left = {
      {
        title = "Files",
        ft = "neo-tree",
        filter = function(buf)
          return vim.b[buf].neo_tree_source == "filesystem"
        end,
      },
    },
    right = {
      { title = "Claude Code %{v:lua.require'ide.claude'.label()}", ft = "claudecode" },
    },
    bottom = {
      {
        title = "Terminal %{b:snacks_terminal.id}",
        ft = "snacks_terminal",
        filter = snacks_at("bottom"),
      },
    },
    options = {
      left = { size = 32 },
      right = {
        size = function()
          return math.floor(vim.o.columns * 0.4)
        end,
      },
      bottom = {
        size = function()
          return math.floor(vim.o.lines * 0.3)
        end,
      },
    },
    animate = { enabled = false },
  },
}
