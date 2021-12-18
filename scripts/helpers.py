from brownie import (
    network,
    accounts,
    config,
    LinkToken,
    MockV3Aggregator,
    VRFCoordinatorMock,
    interface,
    Contract,
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    print(f"active network: {network.show_active()}")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """https://github.com/smartcontractkit/chainlink-mix/blob/master/scripts/helpful_scripts.py#L41

    Will either return the contract address from brownie config,
    or deploy a mock version and return that mock contract

        Args:
            contract_name: (string)

        Returns:
            brownie.network.contract.ProjectContract: The most recent deployed
            version of this contract. -ex. MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        # pick address from the config
        contract_address = config["networks"][network.show_active()][contract_name]
        # return contract(address)
        contract = Contract.from_abi(
            contract_type.name, contract_address, contract_type.abi
        )

    return contract


DECIMALS = 8
INITIAL_VALUE = 4000 * 10 ** DECIMALS


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = accounts[0]
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("deployed")


def fund_with_link(
    to_address, account=None, link_token=None, amount=1 * 10 ** 17
):  # 0.1 LINK
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")

    tx = link_token.transfer(to_address, amount, {"from": account})

    ## Or transfer using the interface
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(amount, to_address, {"from": account})

    tx.wait(1)
    print(f"Contract /{to_address}/ funded with {amount} LINK")
    return tx
