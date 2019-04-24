r"""
Examples:

rebase-remotes.py rebase stable c:\src\git_repo_path\ c:\work\list_with_branches.txt
rebase-remotes.py merge stable c:\src\git_repo_path\ c:\work\list_with_branches.txt
"""

import argparse
import logging
import os
import subprocess
import sys
from functools import wraps

from typing import List

parser = argparse.ArgumentParser()

parser.add_argument('process', help='A required process like rebase, merge or merge_parts')
parser.add_argument('main_branch', help='A required main branch name')
parser.add_argument('project_path', help='A required path to the project')
parser.add_argument('file_with_branches', help='A required path to the file with branches')

# create logger
LOGGER = logging.getLogger('main_logger')
LOGGER.setLevel(logging.DEBUG)

# create formatter for logger
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

# add the handlers to the logger
LOGGER.addHandler(ch)


def print_result(func):
    @wraps(func)
    def wrap(obj, *args, **kwargs):
        """
        :type obj: GitPy
        """
        obj._git('fetch -p')

        conflicts = func(obj, *args, **kwargs)

        result = os.linesep.join(conflicts)
        if not result:
            result = 'No branches with {} conflicts.'.format(func.__name__)

        print('{} result:{}{}'.format(func.__name__, os.linesep, result))

    return wrap


def get_list_of_branches_from_file(file_name):
    with open(file_name) as branch_file, open('ignore.txt') as ignore_file:
        branches = branch_file.readlines()
        ignore_file = ignore_file.readlines()

    ignore_file = set(ignore.strip('\n').upper() for ignore in ignore_file)
    branches = [br.replace('origin/', '').strip() for br in branches]
    branches = [br for br in branches if br.split('/')[0].upper() not in ignore_file]

    assert branches
    return branches


class GitPy(object):

    def __init__(self, main_branch, git_repo_path, file_with_list_of_branches):
        self.main_branch = main_branch  # type: str
        self.git_repo_path = git_repo_path  # type: str
        self.branches = get_list_of_branches_from_file(file_with_list_of_branches)  # type: List[str]

    def _git(self, git_cmd, ignore_err=False, interrupt_if_err=True):  # type: (str, bool, bool) -> bool
        cmd = r'git -C {} {}'.format(self.git_repo_path, git_cmd)
        LOGGER.info(git_cmd)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 1 and not ignore_err:
            LOGGER.warn('{}'.format(output))
            LOGGER.error('{}'.format(error))
            if interrupt_if_err:
                sys.exit(1)

        return not process.returncode

    @print_result
    def rebase(self, push=True):
        conflicts = []
        for branch in self.branches:
            self._git('branch -D {}'.format(branch), ignore_err=True)
            self._git('checkout {}'.format(branch))

            if self._git('pull --rebase origin {}'.format(self.main_branch), interrupt_if_err=False):
                if push:
                    self._git('push -f origin {}'.format(branch))
            else:
                conflicts.append(branch)
                self._git('rebase --abort')

        return conflicts

    @print_result
    def merge(self, target, push=False):
        self._git('checkout {}'.format(self.main_branch))
        self._git('pull')

        if not self._git('checkout {}'.format(target), ignore_err=True):
            LOGGER.info('branch {} not found.'.format(target))
            self._git('checkout {} -b {}'.format(self.main_branch, target))

        conflicts = []
        for branch in self.branches:
            if not self._git('merge {}'.format(branch), interrupt_if_err=False):
                conflicts.append(branch)
                self._git('merge --abort')

        if push:
            self._git('push origin {}'.format(target))

        return conflicts


if __name__ == '__main__':
    args = parser.parse_args()
    rebase_remotes = GitPy(args.main_branch, args.project_path, args.file_with_branches)

    if args.process == 'rebase':
        rebase_remotes.rebase()

    elif args.process == 'merge':
        rebase_remotes.merge('QA4')

    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
