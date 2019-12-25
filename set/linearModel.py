from web3 import Web3

from set.util import print_status, account_from_key, token_transfer, init_linear_channel_state, init_linear_node
from set.contract import deploy_secret_registry, deploy_token_network_registry, mint, create_ERC20Token_network, ERC20_transfer, open_channel, deploy_token, set_initial_deposit
from set.channelState import ChannelState
from time import sleep
import set.key as key
from set.algorism import contract_bundle
import set.settingParameter as p
# geth path setting
ipc_path = '../gethchain/geth.ipc'
w3 = Web3(Web3.IPCProvider(ipc_path))

# node setting
account = []
key_path, key_passphrase = key.get_keys()
for i in range(p.node_count) :
    account.append(account_from_key(w3, key_path[i], key_passphrase[i]))
print_status("account", 0, 0, account)
# print('account1', account[0].address)
# print('account1', account[0].privateKey)
# print('account2', account[1].address)
# print('account2', account[1].privateKey)


#token transfer
for i in range(1, p.node_count) :
    token_transfer(w3, account[0], account[i], 100000000000)

# Deploy SecretRegistry, Token, TokenNetworkRegistry contract
secret_registry_contract = deploy_secret_registry(w3, account[0])
token_contract = deploy_token(w3, account[0])
token_network_registry_contract = deploy_token_network_registry(w3, account[0],
                                    secret_registry_contract.address, p.chain_id, p.settlement_timeout_min, p.settlement_timeout_max, p.max_token_networks)
print_status("secret_registry_contract", 0, 2, secret_registry_contract.address)
print_status("token_contract", 1, 2, token_contract.address)
print_status("token_network_registry_contract", 2, 2, token_network_registry_contract.address)

# mint token contract
to, amount = mint(w3, account[0], token_contract, account[0].address, p.mint_ERC20)
print_status("mint result[to , amount]", 0, 0, to, amount)

# Create TokenNetwork contract
token_network_contract = create_ERC20Token_network(w3, account[0], token_network_registry_contract, token_contract.address, p.channel_participant_deposit_limit, p.token_network_deposit_limit)
print_status("token_network_contract", 0, 0, token_network_contract)

# distribute token
result = {}
for i in range(p.node_count-1) :
    result[i] = ERC20_transfer(w3, account[0], token_contract, account[i+1].address, int(p.mint_ERC20/p.node_count))
    print_status("distribute Token[recipient, amount]", i, p.node_count-2, result[i][0], result[i][1])


# ----------------------------------------------
# 여기서 수정 필요
# ----------------------------------------------


# openChannel
# open_channel(w3, account, contract, participant1, participant2, settle_time = min)
# 2,4,5 번째 인자만 수정하면 된다.
# 2 : smartcontract을 호출할 노드
# 4 : channel을 열 node 1 address
# 5 : channel을 열 node 2 address
channel = {}
for i in range(p.node_count-1) :
    channel[i] = open_channel(w3, account[i], token_network_contract, account[i].address, account[i+1].address, p.settlement_timeout_min)
    print_status("open channel[channel_identifier, participant1, participant2, settle_timeout]", i, p.node_count-2, channel[i][0], channel[i][1], channel[i][2], channel[i][3])

# set Deposit
# 마지막 인자에 deposit한 돈을 setting할 수 있다. 지금은 모두 같게 설정
channel_new_deposit = set_initial_deposit(w3, account, token_network_contract, channel, p.initial_deposit)
# print_status("channel_new_deposit", 0, 0, channel_new_deposit)

# init channel state
# init_linear_channel_state(account, token_network_contract, channel_identifier, secret_registry_contract)
channel_state = init_linear_channel_state(ChannelState, account, token_network_contract.address, channel, channel_new_deposit, secret_registry_contract.address)
# print_status("channel_state{channel_identifier : [channelState[0], channelState[1]]}", 0, 0, channel_state)

# init Node
#init_linear_node(channel_state)
Nodes = init_linear_node(Node, account, channel_state)
# print_status("Nodes", 0, 0, Nodes)

print("======================================")
print("happy case scennario")
print("A -> D (10$)")
print("======================================")

# Contract Propse
print("===================Contract propose===================")
cr = 0
for i in range(3) : 
    message = Nodes[i].send_contract_propose(cr, account[0].address, account[i].address, account[i+1].address, account[3].address, 10)
    Nodes[i+1].receive_contract_propose(message)

print("===================Contract select===================")
# Contract Select
message = Nodes[3].send_contract_select(cr, account[2].address,0,0,0,0)
contract = Nodes[2].receive_contract_select(message)
message = Nodes[2].send_contract_select(cr, account[1].address, contract[0], contract[1], contract[2], contract[3])
contract = Nodes[1].receive_contract_select(message)
message = Nodes[1].send_contract_select(cr, account[0].address, contract[0], contract[1], contract[2], contract[3])
Nodes[0].receive_contract_select(message)

print("===================Locked Transfer===================")
# Locked Transfer
# BP = message_data, additional_hash, balance_hash, signature['signature']
BP = Nodes[0].init_locked_transfer(w3, cr, account[0].address, account[1].address, account[3].address, 10)
secret = Nodes[0].send_secret(cr)
Nodes[3].receive_secret(secret)
Nodes[1].receive_locked_transfer(account[0].address, BP)
BP = Nodes[1].send_locked_transfer(w3, cr, account[0].address, account[2].address, account[3].address, 10, BP.message_data.secrethash)
Nodes[2].receive_locked_transfer(account[1].address, BP)
BP = Nodes[2].send_locked_transfer(w3, cr, account[0].address, account[3].address, account[3].address, 10, BP.message_data.secrethash)
Nodes[3].receive_locked_transfer(account[2].address, BP)

# reveal secret
# print("===================reveal secret===================")
# message = Nodes[3].target_reveal_secret(w3, cr, account[2].address, account[3].address)
# BP = Nodes[2].receive_reveal_secret(w3, message)
# Nodes[3].receive_unlockBP(account[2].address, BP)
# print("===================================================")
# message = Nodes[2].reveal_secret(cr, account[1].address, account[2].address)
# BP = Nodes[1].receive_reveal_secret(w3, message)
# Nodes[2].receive_unlockBP(account[1].address, BP)
# print("===================================================")
# message = Nodes[1].reveal_secret(cr, account[0].address, account[1].address)
# BP = Nodes[0].receive_reveal_secret(w3, message)
# Nodes[1].receive_unlockBP(account[0].address, BP)


# dispute case
print("======================================")
print("dispute case scennario")
print("C does not unlock to D")
print("======================================")

# D Register secret
print("===================Register secret===================")
message = Nodes[3].target_reveal_secret(w3, cr, account[2].address, account[3].address)
Nodes[3].register_secret_to_onchain(w3, cr, account[3], secret_registry_contract)


# D channel close
# print("===================Channel close=====================")
# sleep(4)
# # print("block number : ", w3.eth.blockNumber)
# Nodes[3].close_channel_to_onchain(w3, account[3], token_network_contract, account[2].address)
# # C updateNonClosingBalanceProof
#
# # D settle channel
# print("===================Channel settle====================")
# sleep(10)
# print("block number : ", w3.eth.blockNumber)
# Nodes[3].settle_channel_to_onchain(w3, account[3], token_network_contract, account[2].address)
# # D unlock
# print("===================Channel unlock====================")
# Nodes[3].unlock_to_onchain(w3, account[3], token_network_contract, account[2].address)


# c colse channel with B
Nodes[2].close_channel_to_onchain(w3, account[2], token_network_contract, account[1].address)
# B updateNonClosingBalanceProof

# C settle channel
print("===================Channel settle====================")
sleep(10)
print("block number : ", w3.eth.blockNumber)
Nodes[2].settle_channel_to_onchain(w3, account[2], token_network_contract, account[1].address)
# C unlock
print("===================Channel unlock====================")
Nodes[2].unlock_to_onchain(w3, account[2], token_network_contract, account[1].address)


# print("===================Channel close=====================")
sleep(4)
# print("block number : ", w3.eth.blockNumber)
Nodes[3].close_channel_to_onchain(w3, account[3], token_network_contract, account[2].address)
# C updateNonClosingBalanceProof

# D settle channel
print("===================Channel settle====================")
sleep(10)
print("block number : ", w3.eth.blockNumber)
Nodes[3].settle_channel_to_onchain(w3, account[3], token_network_contract, account[2].address)
# D unlock
print("===================Channel unlock====================")
Nodes[3].unlock_to_onchain(w3, account[3], token_network_contract, account[2].address)

Nodes[2].unlock_to_onchain(w3, account[2], token_network_contract, account[1].address)