def test_rebase_call_order(rebase_remotes, mocker):
    rr = rebase_remotes
    mocker.patch.object(rr, 'git', return_value=1)
    target_branch = 'test'
    rr.rebase(target_branch, False)

    calls = [
        mocker.call('fetch -p'),
        mocker.call('checkout -B {0} origin/{0}'.format('br1')),
        mocker.call('pull --rebase origin {}'.format(target_branch), interrupt_if_err=False),
        mocker.call('checkout -B {0} origin/{0}'.format('br2')),
        mocker.call('pull --rebase origin {}'.format(target_branch), interrupt_if_err=False),
    ]
    rr.git.assert_has_calls(calls, any_order=False)
