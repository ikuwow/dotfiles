# Tool Decisions

This index lists the tools this repository settles on, with the pull requests and issues where each choice was made.
Each entry names the current choice and what it replaced, and the linked bodies carry the reasoning; pull requests from before 2025 mostly record no reasoning.
Claude Code configuration under `claude/` and `claude-plugins/` is outside this index, since its rules and skills state their own policy.

- Platform: macOS on Apple Silicon, with Linux limited to symlink deployment
  - Intel Mac support was dropped in [#494]
- Dotfile deployment: symlinks created by `scripts/deploy.sh`
  - mackup was removed in [#54]
- CI: GitHub Actions
  - Travis CI gave way to CircleCI in [#13], and CircleCI to GitHub Actions in [#17]
- Version manager: mise, with the aqua CLI kept for repositories that need it
  - mise replaced asdf in [#111]
  - aqua was removed in favor of mise's aqua backend in [#116], then re-added in [#125]
  - Global npm tools are declared through mise's `npm:` backend from [#332] on
- Terminal emulator: Ghostty, adopted in [#56]
- Editor: Neovim, configured in `xdg-config/nvim/init.lua`, with Vim as a fallback that reads the shared vimrc ([#572])
  - Plugin manager: vim-plug, which replaced dein.vim in [#44], which in turn replaced NeoBundle in [#3]
  - File tree: nvim-tree, which replaced fern in [#579], which in turn replaced NERDTree in [#38]
  - GUI front end: Neovide, which replaced goneovim in [#72]
  - Claude Code integration: claudecode.nvim, added in [#71]
- IDE setup around Claude Code: compared across candidate setups in [#569]
  - JetBrains IDEs and Junie CLI were removed in [#571]
  - Zed's evaluation in [#568] was closed as a duplicate
  - [#564] and [#570] propose launchers for the candidate setups
- Key remapping: Hammerspoon for the solo ⌘ tap that switches the input mode, replacing Karabiner-Elements in [#415] as planned in [#401]
  - Caps Lock to Control is set in the macOS Modifier Keys panel, since [#415] found no scripted setting that persists across a restart
  - The HHKB's Esc and backtick swap goes through `hidutil` ([#436])
- Containers: colima, plus Apple `container` with socktainer, which [#226] set up
- GitHub CLI extensions: gh-dash ([#276]) and gh-sub-issue, vendored under `gh-extensions/` ([#289])
- Browser customization: userscripts under `userscripts/`, loaded by the Userscripts extension in Safari ([#241]) and by Violentmonkey in Chrome ([#300])
  - x-declutter replaced the Control Panel for Twitter extension in [#495]
- AI commit message drafts: the prepare-commit-msg hook runs `claude -p` on the Claude Code login ([#451])
  - The hook first ran the claude CLI with Haiku ([#177]), then called the Anthropic API ([#179])
  - [#178] measures the latency of the claude CLI route and lists faster backends to try

[#3]: https://github.com/ikuwow/dotfiles/pull/3
[#13]: https://github.com/ikuwow/dotfiles/pull/13
[#17]: https://github.com/ikuwow/dotfiles/pull/17
[#38]: https://github.com/ikuwow/dotfiles/pull/38
[#44]: https://github.com/ikuwow/dotfiles/pull/44
[#54]: https://github.com/ikuwow/dotfiles/pull/54
[#56]: https://github.com/ikuwow/dotfiles/pull/56
[#71]: https://github.com/ikuwow/dotfiles/pull/71
[#72]: https://github.com/ikuwow/dotfiles/pull/72
[#111]: https://github.com/ikuwow/dotfiles/pull/111
[#116]: https://github.com/ikuwow/dotfiles/pull/116
[#125]: https://github.com/ikuwow/dotfiles/pull/125
[#177]: https://github.com/ikuwow/dotfiles/pull/177
[#178]: https://github.com/ikuwow/dotfiles/issues/178
[#179]: https://github.com/ikuwow/dotfiles/pull/179
[#226]: https://github.com/ikuwow/dotfiles/pull/226
[#241]: https://github.com/ikuwow/dotfiles/pull/241
[#276]: https://github.com/ikuwow/dotfiles/pull/276
[#289]: https://github.com/ikuwow/dotfiles/pull/289
[#300]: https://github.com/ikuwow/dotfiles/pull/300
[#332]: https://github.com/ikuwow/dotfiles/pull/332
[#401]: https://github.com/ikuwow/dotfiles/issues/401
[#415]: https://github.com/ikuwow/dotfiles/pull/415
[#436]: https://github.com/ikuwow/dotfiles/pull/436
[#451]: https://github.com/ikuwow/dotfiles/pull/451
[#494]: https://github.com/ikuwow/dotfiles/pull/494
[#495]: https://github.com/ikuwow/dotfiles/pull/495
[#564]: https://github.com/ikuwow/dotfiles/pull/564
[#568]: https://github.com/ikuwow/dotfiles/issues/568
[#569]: https://github.com/ikuwow/dotfiles/issues/569
[#570]: https://github.com/ikuwow/dotfiles/pull/570
[#571]: https://github.com/ikuwow/dotfiles/pull/571
[#572]: https://github.com/ikuwow/dotfiles/pull/572
[#579]: https://github.com/ikuwow/dotfiles/pull/579
