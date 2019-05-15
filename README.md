# Rebase-remotes [![Build Status](https://travis-ci.org/asavras/rebase-remotes.svg?branch=master)](https://travis-ci.org/asavras/rebase-remotes)

Rebase-remotes is a Python cli for rebasing remote branches onto specify branch.
All conflicts need to be resolved manually.

## Usage

```bash
python rebase_remotes.py c:\repo\ c:\list_with_branches.txt -s rebase -b master -p
python rebase_remotes.py c:\repo\ c:\list_with_branches.txt -s merge -b develop -i c:\ignore.txt
```
