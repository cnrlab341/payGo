from web3 import Web3
from set.util import account_from_key, token_transfer, payGo
from set.node import Node
from set.channelState import ChannelState
import set.key as key
from set.structure import hub_result, payer_result
import set.settingParameter as p
from set.algorism import RTT
import time
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

pool = ThreadPool(processes=1000)
def flow_payGo(initiator, target, amount, Omega, Omega_prime, interval, stop, round, start) :
    for i in range(round) :
        pool.apply_async(payGo, (initiator, target, amount, Omega, Omega_prime, i, round, start, interval))

        time.sleep(interval)

        if i == round : return 0

start = time.time()
th1_list = pool.apply_async(flow_payGo, (a, d, 80000, 1,4,2,True, 1000, start))

th_list = pool .apply_async(flow_payGo, (d, a,80000, 1,4,3,False, 1000, start))
th1_list.get()

