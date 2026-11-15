return {
  "coder/claudecode.nvim",
  dependencies = { "folke/snacks.nvim" },
  -- Loaded at startup, so its WebSocket server runs before any Claude Code
  -- starts
  lazy = false,
  keys = {
    { "<leader>ac", "<cmd>ClaudeCode<cr>", desc = "Toggle Claude" },
    { "<leader>af", "<cmd>ClaudeCodeFocus<cr>", desc = "Focus Claude" },
    { "<leader>ar", "<cmd>ClaudeCode --resume<cr>", desc = "Resume Claude" },
    { "<leader>aC", "<cmd>ClaudeCode --continue<cr>", desc = "Continue Claude" },
    { "<leader>ab", "<cmd>ClaudeCodeAdd %<cr>", desc = "Add current buffer" },
    { "<leader>as", "<cmd>ClaudeCodeSend<cr>", mode = "v", desc = "Send to Claude" },
    { "<leader>as", "<cmd>ClaudeCodeTreeAdd<cr>", desc = "Add file", ft = { "neo-tree" } },
    { "<leader>aa", "<cmd>ClaudeCodeDiffAccept<cr>", desc = "Accept diff" },
    { "<leader>ad", "<cmd>ClaudeCodeDiffDeny<cr>", desc = "Deny diff" },
  },
  opts = function()
    return {
      terminal = {
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
