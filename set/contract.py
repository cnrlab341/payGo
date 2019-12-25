from util import compile_contract, wait_contract_address, get_contract, call_function, transact_function, wait_event
from channelState import ChannelState

class smartContract() :
    def __init__(self,w3, creater, chain_id, settlement_timeout_min, settlement_timeout_max, max_token_networks,
                 mint_ERC20, channel_participant_deposit_limit, token_network_deposit_limit, node_count, account):
        self.secret_registry_contract = deploy_secret_registry(w3, creater)
        self.token_contract = deploy_token(w3, creater)
        self.token_network_registry_contract = deploy_token_network_registry(w3, creater,
                                                                        self.secret_registry_contract.address,
                                                                        chain_id, settlement_timeout_min,
                                                                        settlement_timeout_max, max_token_networks)
        mint(w3, creater, self.token_contract, creater.address, mint_ERC20)

        self.token_network_contract = create_ERC20Token_network(w3, creater, self.token_network_registry_contract,
                                                           self.token_contract.address, channel_participant_deposit_limit,
                                                           token_network_deposit_limit)
        for i in range(node_count - 1):
            ERC20_transfer(w3, creater, self.token_contract, account[i + 1].address, int(mint_ERC20 / node_count))
        print("token distribution : ", mint_ERC20 / node_count)

        # create_Channel = (node1, node2, node1_deposit, node2_deposit)
    def create_channel(self, w3, n1, n2, n1_deposit, n2_deposit, settlement_timeout_min):
        # openChannel
        channel = open_channel(w3, n1.account, self.token_network_contract, n1.account.address, n2.account.address, settlement_timeout_min)

        # deposit
        set_deposit(w3, n1.account, self.token_network_contract, n1.account.address, n2.account.address, channel[0], n1_deposit)
        set_deposit(w3, n2.account, self.token_network_contract, n2.account.address, n1.account.address, channel[0], n2_deposit)

        # init channel state
        n1_state = ChannelState(n1.account.privateKey, 0, self.token_network_contract,
                                [n1.account.address, n2.account.address], (n1_deposit, n2_deposit),
                                channel[0], self.secret_registry_contract)
        n2_state = ChannelState(n2.account.privateKey, 1, self.token_network_contract,
                                [n2.account.address, n1.account.address], (n1_deposit, n2_deposit),
                                   channel[0], self.secret_registry_contract)

        # register state in node
        n1.create_channel_state(n2, n1_state)
        n2.create_channel_state(n1, n2_state)

        print("create channel({},{}) : {}, {}".format(n1.name, n2.name, n1_deposit, n2_deposit))

# deploy secret_registry contract and return contract object
def deploy_secret_registry(w3, account) :
    contract_interface = compile_contract('../contracts/SecretRegistry.sol', 'SecretRegistry')
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    transaction = contract.constructor().buildTransaction({
        'nonce': w3.eth.getTransactionCount(account.address),
        'from': account.address
    })
    signed_transaction = w3.eth.account.signTransaction(transaction, account.privateKey)
    tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
    contract_address = wait_contract_address(w3, tx_hash)
    contract = get_contract(w3, contract_address, contract_interface['abi'])

    return contract

# deploy token contract and return contract object
def deploy_token(w3, account) :
    contract_interface = compile_contract('../contracts/Token.sol', 'Token')
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    transaction = contract.constructor().buildTransaction({
        'nonce': w3.eth.getTransactionCount(account.address),
        'from': account.address
    })
    signed_transaction = w3.eth.account.signTransaction(transaction, account.privateKey)
    tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
    contract_address = wait_contract_address(w3, tx_hash)
    contract = get_contract(w3, contract_address, contract_interface['abi'])

    return contract

# deploy token network registry contract and return contract object
# args = secret_registry_contract, chain_id, settlement_timeout_min, settlement_timeout_max
def deploy_token_network_registry(w3, account, *args) :
    contract_interface = compile_contract('../contracts/TokenNetworkRegistry.sol', 'TokenNetworkRegistry')
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    transaction = contract.constructor(args[0], args[1], args[2], args[3], args[4]).buildTransaction({
        'nonce': w3.eth.getTransactionCount(account.address),
        'from': account.address
    })
    signed_transaction = w3.eth.account.signTransaction(transaction, account.privateKey)
    tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)
    contract_address = wait_contract_address(w3, tx_hash)
    contract = get_contract(w3, contract_address, contract_interface['abi'])

    return contract

# mint token
# args = to, amount
def mint(w3, account, contract, *args) :
    transactor = contract.functions["mint"](args[0], args[1])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "Transfer")

    return result[0]['args']['to'], result[0]['args']['value']

# Create token network
# args = token_contract_address, channel_participant_deposit_limit, token_network_deposit_limit
def create_ERC20Token_network(w3, account, contract, *args) :
    contract_interface = compile_contract('../contracts/TokenNetwork.sol', 'TokenNetwork')
    transactor = contract.functions["createERC20TokenNetwork"](args[0], args[1], args[2])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "TokenNetworkCreated")
    contract = get_contract(w3, result[0]['args']['token_network_address'], contract_interface['abi'])
    return contract

# Transfer ERC20 token
# args = address recipient, uint256 amount
def ERC20_transfer(w3, account, contract, *args) :
    transactor = contract.functions["transfer"](args[0], args[1])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "Transfer")
    return result[0]['args']['to'], result[0]['args']['value']


# args = participant1, participant2, settle_time
def open_channel(w3, account, contract, *args):
    transactor = contract.functions["openChannel"](args[0], args[1], args[2])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "ChannelOpened")
    return result[0]['args']['channel_identifier'], result[0]['args']['participant1'], result[0]['args']['participant2'], result[0]['args']['settle_timeout']

# args = channel_state, p.initial_deposit
# need args = channel_identifier, participant, total_deposit, partner
def set_initial_deposit(w3, account, contract, channel, initial_deposit):
    k, result= 0, []
    for i in channel :
        for j in range(1,3) :
            if j == 1 : k +=1
            transactor = contract.functions["setTotalDeposit"](
                channel[i][0], channel[i][j], initial_deposit[k], channel[i][3-j])
            tx_hash = transact_function(w3, account[k], transactor)
            temp = wait_event(w3, contract, tx_hash, "ChannelNewDeposit")
            result.append((temp[0]['args']['channel_identifier'], temp[0]['args']['participant'], temp[0]['args']['total_deposit']))

    return result

def set_deposit(w3, account, contract, n1, n2, channel_identifier, deposit):
    transactor = contract.functions["setTotalDeposit"](
        channel_identifier, n1, deposit, n2)
    tx_hash = transact_function(w3, account, transactor)
    temp = wait_event(w3, contract, tx_hash, "ChannelNewDeposit")
    result = temp[0]['args']['channel_identifier'], temp[0]['args']['participant'], temp[0]['args']['total_deposit']

    return result

def register_secret(w3, account, contract, *args) :
    transactor = contract.functions["registerSecret"](args[0], args[1], args[2], args[3])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "SecretRevealed")
    return result[0]['args']['secrethash'], result[0]['args']['secret'], result[0]['args']['endTime']

def close_channel(w3, account, contract, *args) :
    transactor = contract.functions["closeChannel"](args[0], args[1], args[2], args[3], args[4], args[5], args[6])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "ChannelClosed")
    return result[0]['args']['channel_identifier'], result[0]['args']['closing_participant'], result[0]['args']['nonce']

def update_NonClosingBalanceProof(w3, account, contract, *args) :
    transactor = contract.functions["updateNonClosingBalanceProof"](args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "NonClosingBalanceProofUpdated")
    print("test", result)
    return result[0]['args']['channel_identifier'], result[0]['args']['closing_participant'], result[0]['args']['nonce']

def settle_channel(w3, account, contract, *args) :
    transactor = contract.functions["settleChannel"](args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "ChannelSettled")
    return result[0]['args']['channel_identifier'], result[0]['args']['participant1_amount'], result[0]['args']['participant2_amount']

def unlock(w3, account, contract, *args) :
    transactor = contract.functions["unlock"](args[0], args[1], args[2], args[3])
    tx_hash = transact_function(w3, account, transactor)
    result = wait_event(w3, contract, tx_hash, "ChannelUnlocked")
    print("test : ", result)
    return result[0]['args']['channel_identifier'], result[0]['args']['participant'], result[0]['args']['partner']\
        , result[0]['args']['locksroot'], result[0]['args']['unlocked_amount'], result[0]['args']['unsettled_amount']\
        , result[0]['args']['unsettled_merkle_root'], result[0]['args']['unsettled_merkle_layer'], result[0]['args']['returned_tokens']



def get_channel_state(account, contract, channel_identifier, participant) :
    caller = contract.functions["getChannelState"](channel_identifier, participant)
    a = caller.call({'from': account.address})

# remove list of addresses from whitelist
def remove_from_list(w3, account, contract, addresses):
    return transact_function(w3, account, contract, 'remove', addresses)


# add address to controllers
def add_controller(w3, account, contract, address):
    return transact_function(w3, account, contract, 'addController', address)


# remove address from controllers
def remove_controller(w3, account, contract, address):
    return transact_function(w3, account, contract, 'removeController', address)
