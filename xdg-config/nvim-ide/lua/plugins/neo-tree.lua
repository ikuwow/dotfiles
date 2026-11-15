return {
  "nvim-neo-tree/neo-tree.nvim",
  branch = "v3.x",
  dependencies = {
    "nvim-lua/plenary.nvim",
    "MunifTanjim/nui.nvim",
    "nvim-tree/nvim-web-devicons",
  },
  lazy = false,
  keys = {
    { "<leader>e", "<cmd>Neotree toggle reveal<cr>", desc = "File tree" },
  },
  opts = {
    close_if_last_window = true,
    -- Files opened from the tree go to the editor area, never to a terminal
    -- or a panel that edgy.nvim holds
    open_files_do_not_replace_types = { "terminal", "snacks_terminal", "qf", "edgy" },
    filesystem = {
      filtered_items = { visible = true },
      follow_current_file = { enabled = true },
      use_libuv_file_watcher = true,
    },
    window = { width = 32 },
  },
}
