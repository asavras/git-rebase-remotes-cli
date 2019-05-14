from unittest.mock import MagicMock, call


def test_rebase(rebase_remotes):
    rr = rebase_remotes
    rr.git = MagicMock(return_value=1)
    target_branch = 'test'
    rr.rebase(target_branch, False)

    calls = [
        call('fetch -p'),
        call('checkout -B {0} origin/{0}'.format('br1')),
        call('pull --rebase origin {}'.format(target_branch), interrupt_if_err=False),
        call('checkout -B {0} origin/{0}'.format('br2')),
        call('pull --rebase origin {}'.format(target_branch), interrupt_if_err=False),
    ]
    rr.git.assert_has_calls(calls, any_order=False)
    assert rr.git.call_count == 5
