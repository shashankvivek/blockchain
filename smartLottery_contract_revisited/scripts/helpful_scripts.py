from brownie import accounts,config,network,MockV3Aggregator,Contract,VRFCoordinatorMock, LinkToken

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def get_account(index=None,id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken
}

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0: #if the contract has been deployed
            deploy_mock()
        contract = contract_type[-1] #MockV3Aggregator[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # to create a contract we need two values: address and ABI
        contract = Contract.from_abi(contract_type._name,contract_address,contract_type.abi)
    return contract

DECIMALS = 8
INITIAL_VALUE = 200000000000
def deploy_mock():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS,INITIAL_VALUE,{"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address,{"from": account})

# def fund_with_link(
#     contract_address, account=None, link_token=None, amount=100000000000000000
# ):  # 0.1 LINK
#     account = account if account else get_account()
#     link_token = link_token if link_token else get_contract("link_token")
#     tx = link_token.transfer(contract_address, amount, {"from": account})
#     # link_token_contract = interface.LinkTokenInterface(link_token.address)
#     # tx = link_token_contract.transfer(contract_address, amount, {"from": account})
#     tx.wait(1)
#     print("Fund contract!")
#     return tx

def fund_with_link(contract_address,account=None,link_token=None,amount=100000000000000000): #0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount , {"from": account})
    tx.wait(1)
    print("Funded link to contract")
    return tx
