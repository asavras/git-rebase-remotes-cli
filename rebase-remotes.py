import argparse
import logging
import os
import subprocess
import sys

from typing import List

parser = argparse.ArgumentParser()

parser.add_argument('process', help='A required process like rebase, merge or merge_parts')
parser.add_argument('main_branch', help='A required main branch name')
parser.add_argument('project_path', help='A required path to the project')
parser.add_argument('file_with_branches', help='A required path to the file with branches')

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=logging.StreamHandler(sys.stdout)
)

LOGGER = logging.getLogger('print_to_stdout')


class GitPy(object):

    def __init__(self, main_branch, git_repo_path, file_with_list_of_branches):
        self.main_branch = main_branch  # type: str
        self.git_repo_path = git_repo_path  # type: str
        self.file_path_with_list_of_branches = file_with_list_of_branches  # type: str
        self.branches = self._get_list_of_branches_from_file()  # type: List[str]

    def _get_list_of_branches_from_file(self):
        with open(self.file_path_with_list_of_branches) as f:
            branches = f.readlines()
        return [br.replace('origin/', '').strip() for br in branches]

    def _git(self, arg, interrupt_if_error=True, ignore_error=False):  # type: (str, bool, bool) -> bool
        cmd = r'git -C {} {}'.format(self.git_repo_path, arg)
        LOGGER.info(arg)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 1 and not ignore_error:
            LOGGER.error('stdout| {}'.format(output))
            LOGGER.error('stderr| {}'.format(error))
            if interrupt_if_error:
                sys.exit(1)

        return not process.returncode

    def rebase(self, push=True):
        assert self.branches
        self._git('fetch -p')

        conflicts = []
        for branch in self.branches:
            LOGGER.info('processing {}'.format(branch))

            self._git('branch -D {}'.format(branch), ignore_error=True)
            self._git('checkout {}'.format(branch))

            if self._git('pull --rebase origin {}'.format(self.main_branch), interrupt_if_error=False):
                if push:
                    self._git('push -f origin {}'.format(branch))
                else:
                    continue

            else:
                conflicts.append(branch)
                self._git('rebase --abort')

        result = os.linesep.join(conflicts)
        if not result:
            result = 'No branches with rebase conflicts.'

        print('* Rebase result * {}{}'.format(os.linesep, result))

    def merge(self, target):
        assert self.branches
        self._git('checkout {} -b {}'.format(self.main_branch, target))

        conflicts = []
        for branch in self.branches:
            if not self._git('merge {}'.format(branch), interrupt_if_error=False):
                conflicts.append(branch)
                self._git('merge --abort')

        result = os.linesep.join(conflicts)
        if not result:
            result = 'No branches with merge conflicts.'

        print('* Merge result * {}{}'.format(os.linesep, result))

    def merge_parts(self, parts):  # type: (int) -> None
        assert self.branches
        self.branches.reverse()

        start = 1
        while self.branches:
            branch_name = 'qa_test_{}'.format(start)
            self._git('checkout {} -b {}'.format(self.main_branch, branch_name))

            for idx in range(parts):
                try:
                    br = self.branches.pop()
                except IndexError:
                    break
                else:
                    self._git('merge {}'.format(br))

            # self._git('push origin {}'.format(branch_name))
            LOGGER.info('push origin {}'.format(branch_name))
            start += 1


if __name__ == '__main__':
    args = parser.parse_args()
    rebase_remotes = GitPy(args.main_branch, args.project_path, args.file_with_branches)

    if args.process == 'rebase':
        rebase_remotes.rebase()

    elif args.process == 'merge':
        rebase_remotes.merge('target_branch')

    elif args.process == 'merge_parts':
        rebase_remotes.merge_parts(5)

    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
