import pytest
from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpers import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link, get_account
import time


def test_should_pick_winner_correctly():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    account = get_account()
    lottery = deploy_lottery()

    lottery.startLottery({"from": account})

    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    fund_with_link(lottery.address)

    lottery.endLottery({"from": account})
    # wait for vrf coordinator to return random number
    time.sleep(210)

    assert lottery.recentWinner() == account.address
    assert lottery.balance() == 0
