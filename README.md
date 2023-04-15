# dotfiles

![CI](https://github.com/ikuwow/dotfiles/actions/workflows/ci.yml/badge.svg)

My dear dotfiles.

## Set up your new Mac

* ☑️ Set language and reboot (System Preferences => Language and Region => Click plus button => ...)
* ☑️ Connect to internet
* ☑️ Sign in Apple ID (System Preferences => Click "Sign in" => ...)
* ☑️ Set password of login user (System Preferences => Users and Groups => ...)
* ☑️ Install Developer Tools: `xcode-select --install`

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
ssh-keygen -t rsa -b 4096 -C "ikuwow@gmail.com"
```

Be sure to set passphrase.
