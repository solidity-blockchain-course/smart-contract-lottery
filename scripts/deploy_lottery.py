from brownie import Lottery, network, config
from scripts.helpers import fund_with_link, get_account, get_contract
from web3 import Web3
import time
from datetime import datetime


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("Lottery started !")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    entrance_fee_wei = lottery.getEntranceFee() + 10000
    entering_tx = lottery.enter({"from": account, "value": entrance_fee_wei})
    entering_tx.wait(1)
    print(f"{account.address} entered the lottery with {entrance_fee_wei} wei !")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    # fund the contract w/ LINK
    tx = fund_with_link(lottery.address)
    tx.wait(1)

    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    request_id = ending_tx.events["RequestedRandomness"]["requestId"]
    print(f"randmoness request-id: {request_id}")

    # wait for chainlink randomness query to complete
    time.sleep(300)

    # print(f"starting {datetime.now().strftime('%H:%M:%S')}")
    # while True:
    #     print(lottery.randomness())
    #     time.sleep(5)

    print(f"randomness: {lottery.randomness()}")
    print(f"Lottery ended, recentWinner: {lottery.recentWinner()}")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
