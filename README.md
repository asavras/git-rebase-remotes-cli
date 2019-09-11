# rebase-remotes-cli

Command line interface for rebasing remote branches onto specify branch.
All conflicts need to be resolved manually.

<a href="https://github.com/asavras/rebase-remotes/actions"><img alt="Build Status" src="https://github.com/asavras/rebase-remotes/workflows/build/badge.svg"></a> [![Build Status](https://travis-ci.org/asavras/rebase-remotes.svg?branch=master)](https://travis-ci.org/asavras/rebase-remotes)

## Versions

rebase-remotes-cli works with Python 2.7, 3.4-3.7

## Usage

```bash
python rebase_remotes.py c:\git_repo\ c:\branches.txt -s rebase -b master
python rebase_remotes.py c:\git_repo\ c:\branches.txt -s merge -b develop -i c:\ignore.txt
```
