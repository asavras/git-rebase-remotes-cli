# Rebase-remotes <a href="https://github.com/asavras/rebase-remotes/actions"><img alt="Build Status" src="https://github.com/asavras/rebase-remotes/workflows/build/badge.svg"></a> [![Build Status](https://travis-ci.org/asavras/rebase-remotes.svg?branch=master)](https://travis-ci.org/asavras/rebase-remotes)

Python cli for rebasing remote branches onto specify branch.
All conflicts need to be resolved manually.

## Usage

```bash
python rebase_remotes.py c:\git_repo\ c:\branches.txt -s rebase -b master
python rebase_remotes.py c:\git_repo\ c:\branches.txt -s merge -b develop -i c:\ignore.txt
```
