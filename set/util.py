import solcx
import time
import asyncio
import threading
import os
from multiprocessing.pool import ThreadPool
# def border() :
#     print()
#     print("=====================================================================================")
#     print()
#
# def print_status(name, st, dt, *args) :
#     content = ""
#     for i in range(len(args)) :
#         temp = str(args[i]) + ". "
#         content += temp
#     print("{} : {}".format(name, content))
#     if (st==dt) :
#         border()

# decrypt keystore file and return account
def account_from_key(w3, key_path, passphrase):
    with open(key_path) as key_file:
        key_json = key_file.read()
    private_key = w3.eth.account.decrypt(key_json, passphrase)
    account = w3.eth.account.privateKeyToAccount(private_key)
    return account

# token tranfer
def token_transfer(w3, sender, receiver, amount) :
    tx = w3.eth.account.signTransaction({
        'nonce': w3.eth.getTransactionCount(sender.address),
        'from': sender.address,
        'to': receiver.address,
        'gasPrice': 0,
        'gas': 9000000,
        'value': amount,
    }, sender.privateKey)
    tx_hash = w3.eth.sendRawTransaction(tx.rawTransaction)
    w3.eth.waitForTransactionReceipt(tx_hash)

# compile contract using solcx and return contract interface
def compile_contract(path, name):
    compiled_contacts = solcx.compile_files([path])
    contract_interface = compiled_contacts['{}:{}'.format(path, name)]
    return contract_interface

# return address of fresh created contract using hash returned from deploy_contract
# return None if transaction was not included to block
def created_contract_address(w3, tx_hash):
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    if not tx_receipt:
        return None
    return tx_receipt['contractAddress']


# wait for deploy transaction to be included to block, return address of created contract
def wait_contract_address(w3, tx_hash):
    w3.eth.waitForTransactionReceipt(tx_hash)
    return created_contract_address(w3, tx_hash)


# return contract object using its address and ABI
def get_contract(w3, address, abi):
    return w3.eth.contract(address=address, abi=abi)


# make transaction to contract invoking function, return transaction hash
def transact_function(w3, account, transactor):
    transaction = transactor.buildTransaction({
        'nonce': w3.eth.getTransactionCount(account.address),
        'gas': 9000000,
        'from': account.address
    })
    signed_transaction = w3.eth.account.signTransaction(transaction, account.privateKey)
    tx_hash = w3.eth.sendRawTransaction(signed_transaction.rawTransaction)

    return tx_hash.hex()


# make call to contract function, return the result of call
def call_function(account, contract, function_name, args=None):
    if args:
        caller = contract.functions[function_name](args)
    else:
        caller = contract.functions[function_name]()
    return caller.call({'from': account.address})


# return event data from transaction with hash tx_hash
# return None if transaction was not included to block
def get_event(w3, contract, tx_hash, event_name):
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    if not tx_receipt:
        return None
    return contract.events[event_name]().processReceipt(tx_receipt)

# wait for transaction to be included to block, return event data
def wait_event(w3, contract, tx_hash, event_name):
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return get_event(w3, contract, tx_hash, event_name)


# def payGo(initiator, target, amount):
#     for partner in initiator.partner.keys():
#         th = Thread(target=execute_PayGo, args=(initiator, partner, target, amount))
#         th.start()
# def payGo_pending(initiator, target, amount, start_time, Omega, Omega_prime, round, total_round, lock) :
#     global complete_propose
#     if not complete_propose[initiator.name] :
#         return True
#     else :
#         pool = ThreadPool(processes=1)
#         pool.apply_async(payGo_inner, (initiator, target, amount, start_time, Omega, Omega_prime, round, total_round, lock))
#         return False

def payGo(initiator, target, amount, Omega, Omega_prime, round, total_round, start) :
    start_time = time.time()
    message_bundle = []
    secret = os.urandom(32)
    payment_state = "contractPropose"
    message_bundle += initiator.init_contract_propose(round, initiator, target, amount, secret, start_time, Omega,
                                                      Omega_prime, payment_state, start)
    while True:
        result = []
        # print("[{}] type : {}".format(round, message_bundle[0].id))
        for message in message_bundle:
            if (message.id == "contractPropose"):
                count = check_propose_equal_direction(message_bundle, message.consumer)
                result += message.consumer.receive_contract_propose(message, payment_state, count, Omega,
                                                                        Omega_prime, round)
            elif (message.id == "contractSelect"):
                payment_state = "contractSelect"
                count = check_select_equal_direction(message_bundle, message.producer)
                result += message.producer.receive_contract_select(message, count, payment_state, Omega, round)
            elif (message.id == "contractConfirm"):
                result += message.consumer.receive_contract_confirm(message, round)
            elif (message.id == "contractReject"):
                result += message.parnter.receive_contract_reject(message, round)
            elif (message.id == "sendSecret"):
                payment_state = "lockedTransfer"
                result += message.target.receive_secret(message)
            elif (message.id == "resSecret"):
                result += message.initiator.recevie_res_secret(message, round)
            elif (message.id == "lockedTransfer"):
                result += message.consumer.receive_locked_transfer(message, round)
            elif (message.id == "revealSecret"):
                result += message.producer.receive_reveal_secret(message, round, Omega, Omega_prime, total_round)
            elif (message.id == "resRevealSecret"):
                message.consumer.receive_unlockBP(message, round)
            elif (message.id == "fail"):
                print("payment fail : {}".format(message.content))
        message_bundle = result

        if len(message_bundle) == 0:
            break



def check_select_equal_direction(message_bundle, partner) :
    count = 0
    for message in message_bundle :
        if message.id == "contractSelect" and partner == message.producer :
            count +=1
    return count

def check_propose_equal_direction(message_bundle, partner) :
    count = 0
    for message in message_bundle :
        if message.id == "contractPropose" and partner == message.consumer :
            count +=1
    return count



# # init linear channelState
# # (sk, i, contract, addrs, channel_identifier, secret_registry_contract)
# def init_linear_channel_state(ChannelState, account, token_network_contract, channel, channel_deposit, secret_registry_contract) :
#     channel_state = {}
#     k = 0
#     for i in range(len(channel)) :
#         deposit = channel_deposit[i][2], channel_deposit[i+1][2]
#         channel_state[channel[i][0]] = [
#             ChannelState(account[k].privateKey, 0, token_network_contract, [account[k].address, account[k + 1].address], deposit, channel[i][0], secret_registry_contract),
#             ChannelState(account[k+1].privateKey, 1, token_network_contract, [account[k].address, account[k + 1].address], deposit, channel[i][0], secret_registry_contract)]
#
#         # round 0 create
#         # completeRound(channel_state[channel[i]], 0, 0, 0, 0, 0)
#         k +=1
#
#     return channel_state
#
# # init linear node
# def init_linear_node(Node, account, channel_state):
#     node_channel_state = [list() for _ in account]
#     k = 0
#     for i in channel_state :
#         node_channel_state[k].append(channel_state[i][0])
#         node_channel_state[k+1].append(channel_state[i][1])
#         k +=1
#
#     return [Node(roles) for roles in node_channel_state]
#
