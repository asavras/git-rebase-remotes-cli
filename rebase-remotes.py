import logging
import os
import subprocess
import sys

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
        self.branches = [br.strip() for br in branches]

    def _git(self, arg):  # type: (str) -> int
        cmd = r'git -C {} {}'.format(self.git_repo_path, arg)
        logger.info(cmd)
        process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode != 0:
            logger.error('stdout| {}'.format(output))
            logger.error('stderr| {}'.format(error))

        return True if process.returncode == 0 else False

    def execute(self):  # type: () -> str
        self._get_list_of_branches_from_file()

        if not self._git('fetch -p'):
            return 'Fetch error. Perhaps a problem with the network.'

        for branch in self.branches:
            branch = branch.replace('origin/', '')
            logger.info('Processing - {}'.format(branch))

            self._git('branch -D {}'.format(branch))
            if not self._git('checkout {}'.format(branch)):
                logger.error('Error when switching to branch. Skipping.')
                continue

            if self._git('pull --rebase origin {}'.format(self.main_branch)):
                self._git('push -f origin {}'.format(branch))
            else:
                self.branches_with_conflicts.append(branch)
                self._git('rebase --abort')

        result = os.linesep.join(self.branches_with_conflicts)
        if not result:
            result = 'No branches with conflicts.'

        return result


if __name__ == '__main__':
    # if len(sys.argv) != 3:
    #     sys.stderr.write('argv len err')
    #     sys.exit(1)
    # else:
    #     rebase_remotes = RebaseRemotes(*sys.argv)
    #     print(rebase_remotes.execute())

    from config import MAIN_BRANCH, PROJECT_PATH

    rebase_remotes = RebaseRemotes(MAIN_BRANCH, PROJECT_PATH, 'branches.txt')
    print(rebase_remotes.execute())
