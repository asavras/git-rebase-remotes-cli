# rebase-remotes-cli

Command line interface for rebasing remote branches onto specify branch.
All conflicts need to be resolved manually.

<a href="https://github.com/asavras/rebase-remotes-cli/actions"><img alt="Build Status" src="https://github.com/asavras/rebase-remotes-cli/workflows/build/badge.svg"></a> [![Build Status](https://travis-ci.org/asavras/rebase-remotes-cli.svg?branch=master)](https://travis-ci.org/asavras/rebase-remotes-cli)

## Prerequisites

You'll need the following prior to setup:

* [Git](https://git-scm.com/downloads)

## Versions

rebase-remotes-cli works with Python 2.7, 3.5-3.7

## Usage

```bash
python rebase_remotes.py c:\git_repo\ c:\branches.txt -s rebase -b master
python rebase_remotes.py c:\git_repo\ c:\branches.txt -s merge -b develop -i c:\ignore.txt
```
