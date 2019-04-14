import argparse
import logging
import os
import subprocess
import sys

parser = argparse.ArgumentParser()

parser.add_argument('main_branch', type=str, help='A required main branch name')
parser.add_argument('project_path', type=str, help='A required path to the project')
parser.add_argument('file_with_branches', type=str, help='A required path to the file with branches')

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=logging.StreamHandler(sys.stdout)
)

logger = logging.getLogger('default_logger')


class RebaseRemotes(object):
    """
    Rebase a list of branches onto specified branch letting the conflicts cases to be resolved manually.
    """

    def __init__(self, main_branch, git_repo_path, file_with_list_of_branches):
        self.main_branch = main_branch  # type: str
        self.git_repo_path = git_repo_path  # type: str
        self.file_path_with_list_of_branches = file_with_list_of_branches  # type: str

        self.branches = []
        self.branches_with_conflicts = []

    def _get_list_of_branches_from_file(self):
        with open(self.file_path_with_list_of_branches) as f:
            branches = f.readlines()
        self.branches = [br.replace('origin/', '').strip() for br in branches]

    def _git(self, arg, raise_if_error=True):  # type: (str, bool) -> bool
        cmd = r'git -C {} {}'.format(self.git_repo_path, arg)
        logger.info(cmd)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode:
            logger.error('stdout| {}'.format(output))
            logger.error('stderr| {}'.format(error))
            if raise_if_error:
                raise SystemError

        return not process.returncode

    def execute(self):  # type: () -> str
        self._get_list_of_branches_from_file()

        self._git('fetch -p')

        for branch in self.branches:
            logger.info('Processing branch {}'.format(branch))

            self._git('branch -D {}'.format(branch), raise_if_error=False)
            self._git('checkout {}'.format(branch))

            if self._git('pull --rebase origin {}'.format(self.main_branch), raise_if_error=False):
                self._git('push -f origin {}'.format(branch))
            else:
                self.branches_with_conflicts.append(branch)
                self._git('rebase --abort')

        result = os.linesep.join(self.branches_with_conflicts)
        if not result:
            result = 'No branches with conflicts.'

        return result


if __name__ == '__main__':
    args = parser.parse_args()
    rebase_remotes = RebaseRemotes(args.main_branch, args.project_path, args.file_with_branches)
    br_with_conflicts = rebase_remotes.execute()
    print(br_with_conflicts)
