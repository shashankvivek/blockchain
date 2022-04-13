# 50$ approx 0.014 ETH
#  => 140000000000000000 WEI

from brownie import Lottery, accounts,config, network
from web3 import Web3
import pytest
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link, get_account, get_contract
# from dotenv import load_dotenv

# load_dotenv()

def test_get_entrance_fee():
    # account = accounts[0]
    # lottery = Lottery.deploy(
    #     config["networks"][network.show_active()]["eth_usd_price_feed"],
    #     {"from": account}
    # )
    # assert lottery.getEntranceFee() >  Web3.toWei(0.013,"ether")
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # since we have INITIAL_VALUE as 2000 eth
    # USD entry fee => 50
    # for 50 USD we will need 0.025 ETH
    entrance_fee = lottery.getEntranceFee()
    expected = Web3.toWei(0.025,"ether")
    assert entrance_fee == expected

def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    tx1 = lottery.startLottery({"from": account});
    tx1.wait(1)
    val = lottery.getEntranceFee()
    tx2 = lottery.enter({"from": account,"value": val + 100000000});
    tx2.wait(1)
    assert lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    tx1 = lottery.startLottery({"from": account});
    tx1.wait(1)
    tx2 = lottery.enter({"from": account,"value": lottery.getEntranceFee()});
    tx2.wait(1)
    tx3 = fund_with_link(lottery)
    tx3.wait(1)
    tx4 = lottery.endLottery({"from": account})
    tx4.wait(1)
    assert lottery.lottery_state() == 2

def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    tx1 = lottery.startLottery({"from": account});
    tx1.wait(1)
    lottery.enter({"from": account,"value": lottery.getEntranceFee()});
    lottery.enter({"from": get_account(index=1),"value": lottery.getEntranceFee()});
    lottery.enter({"from": get_account(index=2),"value": lottery.getEntranceFee()});
    fund_with_link(lottery)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    get_contract("vrf_coordinator").callBackWithRandomness(request_id,777,lottery.address,{"from": account})
    # 777 % 3 => 0
    start_bal_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == start_bal_of_account + balance_of_lottery


