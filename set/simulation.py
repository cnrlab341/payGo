from web3 import Web3
from raiden.utils import sha3
from set.util import account_from_key, token_transfer, payGo
import set.contract
# from set.node import Node
# from set.node_balance import Node
from set.node_capacity import Node
# from set.channelState import ChannelState
# from set.channelState_balance import ChannelState
from set.channelState_capacity import ChannelState
import set.key as key
from set.structure import hub_result, payer_result
import set.settingParameter as p
from set.algorism import RTT
import threading
import time, os, random
from set.message import token_network
from multiprocessing.pool import ThreadPool
from multiprocessing import Lock
# geth path setting
ipc_path = '../gethchain/geth.ipc'
w3 = Web3(Web3.IPCProvider(ipc_path))

# Setting node
# the number of node = 30
account = []
key_path, key_passphrase = key.get_keys()
for i in range(p.node_count) :
    account.append(account_from_key(w3, key_path[i], key_passphrase[i]))

# Transfer token
# for i in range(1, p.node_count) :
#     token_transfer(w3, account[0], account[i], 100000000000)

# Setting contract
# w3, creater, chain_id, settlement_timeout_min, settlement_timeout_max, max_token_networks,
#                  mint_ERC20, channel_participant_deposit_limit, token_network_deposit_limit, node_count, account):
# contractManager = contract.smartContract(w3, account[0], p.chain_id, p.settlement_timeout_min, p.settlement_timeout_max,
#                               p.max_token_networks, p.mint_ERC20, p.channel_participant_deposit_limit,
#                               p.token_network_deposit_limit, p.node_count, account);
# Create node

# simulation - create contract a
channel_identifier = 0
def simple_create_channel(n1, n2, n1_deposit, n2_deposit, lock):
    global channel_identifier

    network = token_network("0x" + bytes(20).hex())

    # init channel state
    n1_state = ChannelState(n1.account.privateKey, 0, network,
                            [n1.account.address, n2.account.address], (n1_deposit, n2_deposit),
                            channel_identifier, network, lock)
    n2_state = ChannelState(n2.account.privateKey, 1, network,
                            [n2.account.address, n1.account.address], (n1_deposit, n2_deposit),
                            channel_identifier, network, lock)
    channel_identifier +=1

    # register state in node
    n1.create_channel_state(n2, n1_state)
    n2.create_channel_state(n1, n2_state)

    # print("create channel({},{}) : {}, {}".format(n1.name, n2.name, n1_deposit, n2_deposit))

index = 0
lock = Lock()
result = payer_result()
f1 = RTT()
f2 = RTT()
a = Node(w3, account[index], "A", 0, result, lock,f1,f2)
index +=1
b = []
result = hub_result()
f1 = RTT()
f2 = RTT()
for i in range(10) :
    b.append(Node(w3, account[index], "B" + str(i), 1, result, lock,f1,f2))
    index +=1
c = []
f1 = RTT()
f2 = RTT()
result = hub_result()
for i in range(10) :
    c.append(Node(w3, account[index], "C" + str(i), 2, result, lock,f1,f2))
    index +=1
result = payer_result()
f1 = RTT()
f2 = RTT()
d = Node(w3, account[index], "D", 3, result, lock,f1,f2)

for i in range(10) :
    simple_create_channel(a, b[i], 100000000, 100000, lock)
    for j in range(10) :
        simple_create_channel(b[i], c[j], 100000, 100000, lock)
    simple_create_channel(c[i], d, 100000, 100000000, lock)

def flow_payGo(initiator, target, amount, Omega, Omega_prime, interval, stop, round, start) :

    # if weight :
    #     time_list = [1,3]
    # for i in range(len(time_list)) :
    #     time_list[i] = time_list[i] * weight
    # else :
    #     time_list = [1,1,1,1,1,1,1,1,1,1]
    # random.shuffle(time_list)
    index = 0
    for i in range(round) :
        pool = ThreadPool(processes=1)
        pool.apply_async(payGo, (initiator, target, amount, Omega, Omega_prime, i, round, start, interval))
        # time.sleep(time_list[index])
        time.sleep(interval)
        # index +=1
        # if index == 3 and stop:
            # random.shuffle(time_list)
            # time.sleep(1.5)
            # index = 0
        # print(index, time_list[index])
        if i == round : return 0
#
# sensitiy change : check 사항
# 1. onchain access : aux
# 2. margin, init value pending delay
# 3. aux count
# 4. min probability
pool1 = ThreadPool(processes=1000)
start = time.time()
th1_list = pool1.apply_async(flow_payGo, (a, d, 80000, 1,3.5,1,True, 2000, start))
th_list = pool1.apply_async(flow_payGo, (d, a,80000, 1,3.5,1.3,False, 2000, start))
th1_list.get()
# 35000, 24000

# n = 1
# for i in range(n) :
#     payGo(a,d,70000,1,3.5,i,n,0,1)
#     payGo(d,a,70000,1,3,i,n,0)

