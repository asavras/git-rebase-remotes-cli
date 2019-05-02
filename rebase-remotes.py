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

parser = argparse.ArgumentParser()

parser.add_argument('process', help='A required process like rebase, merge or merge_parts')
parser.add_argument('main_branch', help='A required main branch name')
parser.add_argument('git_repo_path', help='A required path to the project')
parser.add_argument('file_with_branches', help='A required path to the file with branches')

# create logger
logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)

# create formatter for logger
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(ch)


def print_result(func):
    @wraps(func)
    def wrap(obj, *args, **kwargs):
        """
        :type obj: GitFlow
        """
        obj._git('fetch -p')

        conflicts = func(obj, *args, **kwargs)

        result = os.linesep.join(conflicts)
        if not result:
            result = 'No branches with {} conflicts.'.format(func.__name__)

        print('{} result:{}{}'.format(func.__name__, os.linesep, result))

    return wrap


def get_list_of_branches_from_file(file_name):  # type: (str) -> list
    with open(file_name) as f:
        branches = f.readlines()

    branches = [br.replace('origin/', '').strip() for br in branches]

    ignore_file_name = 'ignore.txt'
    if os.path.isfile(ignore_file_name):
        with open(ignore_file_name) as f:
            ignore_file = f.readlines()

        ignore_file = set(ignore.strip('\n').upper() for ignore in ignore_file)
        branches = [br for br in branches if br.split('/')[0].upper() not in ignore_file]

    assert branches
    return branches


class GitFlow(object):

    def __init__(self, main_branch, git_repo_path, file_with_list_of_branches):
        self.main_branch = main_branch  # type: str
        self.git_repo_path = 'git -C {}'.format(git_repo_path)  # type: str
        self.branches = get_list_of_branches_from_file(file_with_list_of_branches)  # type: list

    def _git(self, cmd, ignore_err=False, interrupt_if_err=True):  # type: (str, bool, bool) -> bool
        execute = ' '.join((self.git_repo_path, cmd))
        logger.info(cmd)
        process = subprocess.Popen(execute.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 1 and not ignore_err:
            logger.warn('{}'.format(output))
            logger.error('{}'.format(error))
            if interrupt_if_err:
                sys.exit(1)

        return not process.returncode

    @print_result
    def rebase(self, push=False):
        conflicts = []
        for branch in self.branches:
            self._git('checkout -B {0} origin/{0}'.format(branch))

            if self._git('pull --rebase origin {}'.format(self.main_branch), interrupt_if_err=False):
                if push:
                    self._git('push -f origin {}'.format(branch))
            else:
                conflicts.append(branch)
                self._git('rebase --abort')

        return conflicts

    @print_result
    def merge(self, target):
        if not self._git('checkout {}'.format(target), ignore_err=True):
            logger.warn('branch {} not found.'.format(target))
            sys.exit(1)

        conflicts = []
        for branch in self.branches:
            if not self._git('merge --no-ff {}'.format(branch), interrupt_if_err=False):
                conflicts.append(branch)
                self._git('merge --abort')

        return conflicts


if __name__ == '__main__':
    args = parser.parse_args()
    rebase_remotes = GitFlow(args.main_branch, args.git_repo_path, args.file_with_branches)

    if args.process == 'rebase':
        rebase_remotes.rebase()

    elif args.process == 'merge':
        rebase_remotes.merge('target-branch')

    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
