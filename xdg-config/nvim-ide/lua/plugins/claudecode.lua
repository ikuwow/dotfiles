return {
  "coder/claudecode.nvim",
  dependencies = { "folke/snacks.nvim" },
  -- Loaded at startup, so its WebSocket server runs before any Claude Code
  -- starts
  lazy = false,
  keys = {
    { "<leader>ac", "<cmd>ClaudeCode<cr>", desc = "Toggle Claude" },
    { "<leader>af", "<cmd>ClaudeCodeFocus<cr>", desc = "Focus Claude" },
    { "<leader>an", function() require("ide.claude").new() end, desc = "New Claude session" },
    { "<leader>ar", function() require("ide.claude").new("--resume") end, desc = "Resume in a new session" },
    { "<leader>aC", function() require("ide.claude").new("--continue") end, desc = "Continue in a new session" },
    { "<leader>a]", function() require("ide.claude").cycle(1) end, desc = "Next Claude session" },
    { "<leader>a[", function() require("ide.claude").cycle(-1) end, desc = "Previous Claude session" },
    { "<leader>ab", "<cmd>ClaudeCodeAdd %<cr>", desc = "Add current buffer" },
    { "<leader>as", "<cmd>ClaudeCodeSend<cr>", mode = "v", desc = "Send to Claude" },
    { "<leader>as", "<cmd>ClaudeCodeTreeAdd<cr>", desc = "Add file", ft = { "neo-tree" } },
    { "<leader>aa", "<cmd>ClaudeCodeDiffAccept<cr>", desc = "Accept diff" },
    { "<leader>ad", "<cmd>ClaudeCodeDiffDeny<cr>", desc = "Deny diff" },
  },
  opts = function()
    return {
      terminal = {
        provider = require("ide.claude"),
        split_side = "right",
        split_width_percentage = 0.4,
      },
      env = require("ide.env").child(),
      -- A diff opens in a tab of its own, so the panels around the editor
      -- keep their sizes
      diff_opts = {
        layout = "horizontal",
        open_in_new_tab = true,
      },
    }
  end,
}
