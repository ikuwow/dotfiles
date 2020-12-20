# dotfiles

[![CircleCI](https://circleci.com/gh/ikuwow/dotfiles.svg?style=svg)](https://circleci.com/gh/ikuwow/dotfiles)

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
