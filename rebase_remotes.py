import argparse
import logging
import os
import subprocess
import sys
from functools import wraps

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def get_args():
    examples = r"""
    examples:
    python rebase_remotes.py c:\repo\ c:\list_with_branches.txt -s rebase -b master -p
    python rebase_remotes.py c:\repo\ c:\list_with_branches.txt -s merge -b develop -i c:\ignore.txt
    """
    parser = argparse.ArgumentParser(description='Rebase Remotes Tool',
                                     epilog=examples,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('git_repo_path', help='path to the git repository')
    parser.add_argument('file_with_branches', help='path to the file with list of branches')
    parser.add_argument('-s', help='git strategy', choices=('rebase', 'merge'), required=True)
    parser.add_argument('-b', help='choose specify branch', required=True)
    parser.add_argument('-i', help='path to the file with list of needs to ignore', default='')
    parser.add_argument('-p', help='push target branches to origin repo', default=False, action='store_true')
    return parser.parse_args()


def cli():
    args = get_args()

    assert os.path.isdir(args.git_repo_path), 'Directory does not exist'
    assert os.path.isfile(args.file_with_branches), 'File does not exist'

    rr = RebaseRemotes(args.git_repo_path, args.file_with_branches, args.i)

    if args.s == 'rebase':
        rr.rebase(args.b, args.p)

    elif args.s == 'merge':
        rr.merge(args.b)


def print_result(func):
    @wraps(func)
    def wrap(obj, *args, **kwargs):  # type: (RebaseRemotes, tuple, dict) -> None
        conflicts = func(obj, *args, **kwargs)
        result = os.linesep.join(conflicts)
        if not result:
            result = 'No branches with {} conflicts.'.format(func.__name__)

        sys.stdout.write('{} result:{}{}'.format(func.__name__, os.linesep, result))

    return wrap


class RebaseRemotes(object):

    def __init__(self, git_repo_path, file_with_list_of_branches, ignore_file_name):  # type: (str, str, str) -> None
        self._git_repo_path = 'git -C {}'.format(git_repo_path)
        self._branches = self.get_list_of_branches_from_file(file_with_list_of_branches, ignore_file_name)

    def git(self, cmd, ignore_err=False, interrupt_if_err=True):  # type: (str, bool, bool) -> bool
        execute = ' '.join((self._git_repo_path, cmd))
        logger.info(cmd)
        process = subprocess.Popen(execute.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 1 and not ignore_err:
            logger.warn('{}'.format(output))
            logger.error('{}'.format(error))
            if interrupt_if_err:
                sys.exit(1)

        return not process.returncode

    @staticmethod
    def get_list_of_branches_from_file(file_name, ignore_file_name):  # type: (str, str) -> list
        with open(file_name) as f:
            branches = f.readlines()

        branches = [br.replace('origin/', '').strip() for br in branches]

        if os.path.isfile(ignore_file_name):
            branches = RebaseRemotes.filter_list_of_branches(ignore_file_name, branches)

        assert branches, 'List of branches is empty'
        return branches

    @staticmethod
    def filter_list_of_branches(ignore_file_name, branches):  # type: (str, list) -> list
        with open(ignore_file_name) as f:
            ignore_file = f.readlines()

        ignore_file = set(ignore.strip('\n').upper() for ignore in ignore_file)
        return [br for br in branches if br.split('/')[0].upper() not in ignore_file]

    @print_result
    def rebase(self, onto_branch, push):  # type: (str, bool) -> list
        """
        return: List of conflicting branches for solving them later manually
        """
        self.git('fetch -p')
        conflicts = []
        for branch in self._branches:
            self.git('checkout -B {0} origin/{0}'.format(branch))

            if self.git('pull --rebase origin {}'.format(onto_branch), interrupt_if_err=False):
                if push:
                    self.git('push -f origin {}'.format(branch))
            else:
                conflicts.append(branch)
                self.git('rebase --abort')

        return conflicts

    @print_result
    def merge(self, target):  # type: (str) -> list
        """
        return: List of conflicting branches for solving them later manually
        """
        if not self.git('checkout {}'.format(target), ignore_err=True):
            logger.fatal('branch {} not found.'.format(target))
            sys.exit(1)

        conflicts = []
        for branch in self._branches:
            if not self.git('merge --no-ff {}'.format(branch), interrupt_if_err=False):
                conflicts.append(branch)
                self.git('merge --abort')

        return conflicts


if __name__ == '__main__':
    cli()
