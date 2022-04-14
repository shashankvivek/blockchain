
import time
from scripts.helpful_scripts import fund_with_link, get_account, get_contract
from brownie import Lottery, config , network


def deploy_lottery():
    account = get_account()
    print(" @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print(account)
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify",False)
    )
    print("Deployed Lottery")
    return lottery

def start_lottery():
    account = get_account();
    lottery = Lottery[-1]
    tx = lottery.startLottery(({"from": account}))
    tx.wait(1)
    print("Lottery has started")

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    val = lottery.getEntranceFee() + 1000000000
    endTx = lottery.enter({"from": account, "value": val})
    endTx.wait(1)
    print("Lottery Entered")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1] 
    tx = fund_with_link(lottery)
    tx.wait(1)
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the winner")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()