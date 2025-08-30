# dotfiles

![CI](https://github.com/ikuwow/dotfiles/actions/workflows/ci.yml/badge.svg)

My dear dotfiles.

## Set up your new Mac

### Initial Setup (usually done in setup wizard)
Complete these during initial Mac setup or from System Preferences (reboot required if changed later):
* ☑️ Update macOS to the latest version
* ☑️ Set language
* ☑️ Connect to internet
* ☑️ Sign in with Apple ID
* ☑️ Set password for login user

### Required Manual Steps
* ☑️ Install Developer Tools: `xcode-select --install`
* ☑️ Grant Full Disk Access to Terminal (System Preferences => Privacy & Security => Privacy => Full Disk Access => Add Terminal.app)

## Boostrapping

```
curl -L https://raw.githubusercontent.com/ikuwow/dotfiles/master/bootstrap.sh | bash -s
```

When you want to bootstrap specific branch:

```
curl -L https://raw.githubusercontent.com/ikuwow/dotfiles/master/bootstrap.sh | bash -s -- branchname
```

## Set login shell after bootstrapping

```
# Intel
LOGIN_SHELL="/usr/local/bin/bash"
sudo sh -c "echo $LOGIN_SHELL >> /etc/shells"
chsh -s "$LOGIN_SHELL"
```

```
# Apple Silicon
LOGIN_SHELL="/opt/homebrew/bin/bash"
sudo sh -c "echo $LOGIN_SHELL >> /etc/shells"
chsh -s "$LOGIN_SHELL"
```

## Notes

### Create key pair

```
ssh-keygen -t ed25519 -C "ikuwow@gmail.com"
```

Be sure to set passphrase.
