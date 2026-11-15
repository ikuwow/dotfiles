return {
  "akinsho/bufferline.nvim",
  dependencies = { "nvim-tree/nvim-web-devicons" },
  lazy = false,
  keys = {
    { "<leader>bd", function() Snacks.bufdelete() end, desc = "Delete buffer" },
    { "<leader>bo", function() Snacks.bufdelete.other() end, desc = "Delete other buffers" },
  },
  opts = {
    options = {
      close_command = function(buf)
        Snacks.bufdelete(buf)
      end,
      always_show_bufferline = true,
      offsets = {
        { filetype = "neo-tree", text = "Files", separator = true },
      },
    },
  },
}
