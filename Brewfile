# rubocop:disable all

def is_m1?
  system("uname -m | grep arm64")
end

tap "homebrew/cask"
tap "homebrew/autoupdate"
tap "ikuwow/ikuwow-sshrc"

brew "mas"
brew "mackup"

# First required
mas "Things3", id: 904280696
mas "Bear", id: 1091189122
cask "1password"
mas "1Password for Safari", id: 1569813296
mas "WiFi Signal", id: 525912054
cask "karabiner-elements"
cask "iterm2"
cask "itermai"
cask "pastebot"
cask "istat-menus"
cask "rambox"
cask "bartender"
mas "nordvpn", id: 905953485
mas "WireGuard", id: 1451685025
brew "bash"
cask "logi-options+"
# This installation process hangs up!
# Install by yourself from: https://www.logitechg.com/en-us/innovation/g-hub.html
# cask "logitech-g-hub"
cask "jetbrains-toolbox"
cask "adguard"

brew "coreutils"
brew "diffutils"
brew "findutils"
brew "gnu-sed"
brew "gnu-which"
brew "gawk"
brew "grep"

# required by vim
brew "python"
brew "node@20" # for Copilot

# For AWS
brew "awscli"
brew "awslogs"
brew "cfn-lint"
cask "session-manager-plugin"

brew "zlib"
brew "asdf"
brew "openssl"
brew "telnet"
brew "bash-completion@2"
brew "cloog"
brew "gcc"
brew "cmake"
brew "ghostscript"
brew "git"
brew "git-secrets"
brew "highlight"
brew "jq"
brew "nkf"
brew "nmap"
brew "pwgen"
brew "ikuwow/ikuwow-sshrc/sshrc"
brew "tmux"
brew "trash"
brew "tree"
brew "wget"
brew "watch"
brew "fontforge"
brew "neovim"
brew "graphviz"
brew "shellcheck"
brew "slackcat"
brew "circleci"
brew "actionlint"
brew "yamllint"
brew "imagemagick"
brew "shfmt"
brew "ccat"
brew "ghq"
brew "fzf"
brew "percona-toolkit"
brew "noti"
brew "pre-commit"
brew "act"
brew "tfmigrate"
brew "tflint"
brew "python-yq" # Not "yq"
brew "gh"
brew "kafka"
brew "akamai"
brew "cloudflare-cli4"
brew "direnv"
brew "packer"

# Databases
brew "mysql"
cask "mysqlworkbench"
brew "postgresql@14"
brew "tbls"
brew "sqlparse"

# For gpg key
brew "gpg"
cask "gpg-suite-no-mail"

# For PHP
brew "libsodium"
brew "bison"
brew "re2c"
brew "libiconv"
brew "libzip"

# Virtual environment:
brew "qemu"
brew "libvirt"
# This needs `HOMEBREW_NO_VERIFY_ATTESTATIONS=1`
# See: https://github.com/Homebrew/homebrew-core/issues/177384
brew "virt-manager"

# docker/k8s etc.
tap "fluxcd/tap"
brew "docker"
brew "docker-compose"
brew "docker-buildx"
brew "colima"
brew "kubie"
brew "k9s"
brew "kind"
brew "fluxcd/tap/flux"
brew "helm"
brew "helmfile"
brew "copilot" # AWS Copilot
# kubectl and kustomize should be managed by asdf

# Browsers
cask "google-chrome"
cask "microsoft-edge"
cask "firefox"
cask "deepl"

cask "1password-cli"
cask "vimr"
cask "xquartz"
cask "google-cloud-sdk"
cask "vagrant"
cask "vlc"
cask "zoom"
cask "chromedriver"
cask "lastfm"
cask "ears"
cask "powershell"
cask "onyx"
cask "chatgpt" if is_m1?
cask "utm"

# Work related
cask "miro"
cask "notion"
cask "microsoft-teams"

mas "Dark Reader for Safari", id: 1438243180
mas "The Unarchiver", id: 425424353
mas "Numbers", id: 409203825
mas "Keynote", id: 409183694
mas "Pages", id: 409201541
mas "Omnivore", id: 1564031042
mas "Day One", id: 1055511498
mas "New File Menu", id: 1064959555
mas "Kindle", id: 302584613
mas "LINE", id: 539883307
mas" RapidRes", id: 1329898474
mas "Streaks", id: 963034692
mas "Speedtest", id: 1153157709
mas "そら案内", id: 599799247
mas "Focus", id: 777233759
mas "Control Panel for Twitter", id: 1668516167
mas "one sec", id: 1532875441
mas "Xcode", id: 497799835
