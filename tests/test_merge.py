import pytest


def test_merge_call_order(rebase_remotes, mocker):
    mocker.patch.object(rebase_remotes, 'git', return_value=1)
    rr = rebase_remotes
    target_branch = 'test'
    rr.merge(target_branch)

    calls = [
        mocker.call('checkout {}'.format(target_branch), ignore_err=True),
        mocker.call('merge --no-ff {}'.format('br1'), interrupt_if_err=False),
        mocker.call('merge --no-ff {}'.format('br2'), interrupt_if_err=False),
    ]
    rr.git.assert_has_calls(calls, any_order=False)


def test_merge_fail_checkout(rebase_remotes, mocker):
    mocker.patch.object(rebase_remotes, 'git', return_value=0)
    rr = rebase_remotes
    target_branch = 'test'

    calls = [
        mocker.call('checkout {}'.format(target_branch), ignore_err=True),
    ]
    with pytest.raises(SystemExit):
        rr.merge(target_branch)
    rr.git.assert_has_calls(calls, any_order=False)


def test_merge_not_result(rebase_remotes, mocker):
    mocker.patch.object(rebase_remotes, 'git', return_value=1)
    rr = rebase_remotes
    result = rr.merge('test')
    assert not result
