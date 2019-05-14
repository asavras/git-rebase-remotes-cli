import os
from unittest.mock import MagicMock, call

import pytest


@pytest.fixture
def rebase_remotes(tmpdir):
    git_repo = tmpdir.mkdir('git_repo')

    br_list = tmpdir.mkdir('sub').join('br_list.txt')
    br_list.write(os.linesep.join(('br1',)))

    from rebase_remotes import RebaseRemotes
    yield RebaseRemotes(git_repo.strpath, br_list.strpath, '')
    git_repo.remove()
    br_list.remove()


def test_rebase(rebase_remotes):
    rr = rebase_remotes
    rr.git = MagicMock(return_value=1)
    target_branch = 'test'
    rr.rebase(target_branch, False)

    calls = [
        call('fetch -p'),
        call('checkout -B {0} origin/{0}'.format('br1')),
        call('pull --rebase origin {}'.format(target_branch), interrupt_if_err=False),
    ]
    rr.git.assert_has_calls(calls, any_order=False)
    assert rr.git.call_count == 3
