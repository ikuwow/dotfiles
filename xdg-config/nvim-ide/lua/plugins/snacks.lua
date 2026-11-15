return {
  "folke/snacks.nvim",
  priority = 1000,
  lazy = false,
  keys = {
    { "<leader><space>", function() Snacks.picker.files() end, desc = "Find files" },
    { "<leader>/", function() Snacks.picker.grep() end, desc = "Grep" },
    { "<leader>,", function() Snacks.picker.buffers() end, desc = "Buffers" },
  },
  opts = {
    bigfile = { enabled = true },
    picker = { enabled = true },
  },
}
