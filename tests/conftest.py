import pytest


@pytest.fixture
def rebase_remotes(tmpdir):
    git_repo = tmpdir.mkdir('git_repo')

    br_list = tmpdir.mkdir('sub').join('br_list.txt')
    br_list.write('\n'.join(('br1', 'br2')))

    from rebase_remotes import RebaseRemotes
    yield RebaseRemotes(git_repo.strpath, br_list.strpath, '')
    git_repo.remove()
    br_list.remove()
