from raiden.utils import sha3
from raiden.transfer.merkle_tree import compute_layers, merkleroot
from raiden.transfer.state import MerkleTreeState
from message import LockedTransfer_structure, unlockTransfer
from raiden.utils.signing import pack_data
from structure import balanceProof
from algorism import RTT
from settingParameter import time_meaningful_constant, contract_meaningful_delay_constant, decrese_weight, arise_weight, payGo_contract_meaningful_delay_constant
import time

class ChannelState():
    def __init__(self, sk, i, tokenNetwork, addrs, deposit, channel_identifier, secret_registry_contract, lock):
        self.sk = sk
        self.i = i
        self.token_network = tokenNetwork
        self.addrs = addrs
        self.deposit = deposit
        self.moving_average_capacity = list(deposit)
        self.channel_identifier = channel_identifier
        self.secret_registry_contract = secret_registry_contract
        self.status = "OK"
        self.nonce = 0
        self.transferred_amount = [0,0]
        self.locked_amount = [0,0]
        self.locksroot = [pack_data(['uint256'],[0]),pack_data(['uint256'],[0])]
        self.leaves = [{},{}]
        self.BP = [0,0]
        self.chain_id = 337
        self.RTT = RTT()
        self.pending_payment = [{},{}]
        self.reserve_payment = [{}, {}]
        self.wait_confirm = [{},{}]
        self.lock = lock
        self.payment_history = [[],[]]
        self.weight = 0.6
        self.contract_boundary = [0,0]

    def get_payment_history(self):
        self.lock.acquire()
        try :
            temp = self.payment_history[self.i]
        finally:self.lock.release()
        return temp

    def get_delay_from_payment_history(self, amount, current_time, Max_delay):
        payment_history = self.get_payment_history()
        temp_add = 0
        delay = 0
        for i in range(len(payment_history)) :
            temp_delay = current_time - payment_history[i][1]
            temp_add += payment_history[i][0]
            temp_result = self.temp_add_average_capacity(temp_add, arise_weight)

            if temp_result >= amount :
                delay = temp_delay
                break

        return delay

    def pop_payment_history(self, index):
        try:
            self.payment_history[self.i].pop(index)
        except :
            print("pop error")


    def update_payment_history(self, amount, time):
        self.lock.acquire()
        try :
            self.payment_history[self.i].insert(0, [amount, time])

        finally: self.lock.release()

    def get_pending_payment(self):
        return self.pending_payment[self.i]

    def add_pending_payment(self, cr, newPay):
        self.pending_payment[self.i][cr] = newPay

    def pop_pending_payment(self, cr):
        self.pending_payment[self.i].pop(cr)

    def get_pending_payment_count(self):
        self.lock.acquire()
        try:
            reserve = self.pending_payment[self.i]
        finally:
            self.lock.release()

        return len(reserve.keys())

    def set_reserve_payment(self, cr, amount):
        self.lock.acquire()
        try :
            self.reserve_payment[self.i][cr] = amount
        finally:self.lock.release()

    def pop_reserve_payment(self, cr):
        self.lock.acquire()
        try :
            self.reserve_payment[self.i].pop(cr)
        finally:self.lock.release()

    def get_reserve_payment(self):
        self.lock.acquire()
        try :
            reserve = self.reserve_payment[self.i]
        finally:self.lock.release()

        amount = 0
        for cr in reserve:
                amount += reserve[cr]

        return amount

    def get_reserve_payment_count(self):
        self.lock.acquire()
        try:
            reserve = self.reserve_payment[self.i]
        finally:
            self.lock.release()

        return len(reserve.keys())

    def set_wait_confirm(self, cr, amount, start_time):
        self.lock.acquire()
        try :
            self.wait_confirm[self.i][cr] = amount, start_time
        finally:self.lock.release()

    def get_wait_confirm(self):
        self.lock.acquire()
        try :
            return self.wait_confirm[self.i]
        finally:self.lock.release()

        # if amount > 0 :
    def pop_wait_confirm(self, cr):
        self.lock.acquire()
        try :
            self.wait_confirm[self.i].pop(cr)
        finally:self.lock.release()

    def get_wait_confirm_count(self):
        wait_confirm = self.get_wait_confirm()

        return len(wait_confirm.keys())

    def check_balance(self, amount, current_time, RTT):
        awit_amount = self.update_awaitAmount(RTT)
        reserve_amount = self.get_reserve_payment()
        self.lock.acquire()
        try :
            result = self.deposit[self.i] - self.transferred_amount[self.i] + \
                     self.transferred_amount[1-self.i] - self.locked_amount[self.i] - reserve_amount - awit_amount

            if result >= amount:
                return True, 0
            else:
                # locked_amount, selected_delay, startTime
                pending_payment_bundle = self.pending_payment[self.i]
                delay = 0
                # print("pending_payment", pending_payment)
                for cr in list(pending_payment_bundle) :
                    try:
                        pending_payment = pending_payment_bundle[cr]
                    except:
                        print(
                            "[error 2] item : {}, pending_payment_bundle : {}".format(cr, pending_payment_bundle))
                        continue
                    # print("len pending_payment", len(pending_payment))
                    new_delay =  (pending_payment[1] / contract_meaningful_delay_constant) - \
                            (current_time - pending_payment[2]) / time_meaningful_constant
                    # print("new_delay", new_delay, current_time)
                    if new_delay>= 0 :
                            delay = delay + new_delay
                            result = result + pending_payment[0]
                            if result >= amount :
                                return True, delay
                return False, 0
        finally:
            self.lock.release()

    def check_capacity(self, amount):
        if self.get_average_capacity() >= amount :
            return True
        else :
            return False

    def check_balance2(self, amount):
        a = False
        self.lock.acquire()
        try :
            result = self.deposit[self.i] - self.transferred_amount[self.i] + \
                     self.transferred_amount[1-self.i] - self.locked_amount[self.i]

            if result >= amount:
                self.locked_amount[self.i] += amount
                a = True
        finally:
            self.lock.release()

        return a

    def update_average_capacity(self, newPay, weight):
        self.lock.acquire()
        try:
            temp = self.moving_average_capacity[self.i] * weight + \
                   (self.moving_average_capacity[self.i] + newPay) * (1 - weight)
            # if temp <= 0 :
            #     self.moving_average_capacity[self.i] = 0
            # else :
            self.moving_average_capacity[self.i] = temp

        finally:
            self.lock.release()

    def update_contract_boundary(self, newBoundary):
        self.lock.acquire()
        try:
            if self.contract_boundary[self.i] == 0 :
                self.contract_boundary[self.i] = newBoundary
            else :
                self.contract_boundary[self.i] = self.contract_boundary[self.i] * self.weight + \
                                                 newBoundary * (1 - self.weight)
        finally:
            self.lock.release()

        return self.contract_boundary[self.i]

    def temp_add_average_capacity(self, newPay, weight):
        self.lock.acquire()
        try:
            temp = self.moving_average_capacity[self.i] * weight + \
                   (self.moving_average_capacity[self.i] + newPay) * (1 - weight)
        finally:self.lock.release()

        return temp

    # 수정 여기부터!
    def update_average_capacity_awaitAmount(self, cr, newPay, startTime):
        self.update_average_capacity(-newPay, decrese_weight)
        self.set_wait_confirm(cr, newPay, startTime)

        return self.get_average_capacity()

    def get_average_capacity(self):
        self.lock.acquire()
        try:
            return self.moving_average_capacity[self.i]
        finally: self.lock.release()

    def update_awaitAmount(self, RTT):
        wait_confirm = self.get_wait_confirm()
        amount = 0
        for cr in list(wait_confirm):
            try:
                if RTT < time.time() - wait_confirm[cr][1]:
                    self.update_average_capacity(wait_confirm[cr][0], decrese_weight)
                    self.wait_confirm[self.i].pop(cr)
                else :
                    amount += wait_confirm[cr][0]
            except:
                continue
        return amount

    def test_get_balance(self):
        self.lock.acquire()
        try :
            result = self.deposit[self.i] - self.transferred_amount[self.i] + \
                     self.transferred_amount[1 - self.i] - self.locked_amount[self.i]
        finally: self.lock.release()
        return result

    def test_get_balance2(self, RTT):
        awit_amount = self.update_awaitAmount(RTT)
        reserve_amount = self.get_reserve_payment()
        self.lock.acquire()
        try :
            result = self.deposit[self.i] - self.transferred_amount[self.i] + \
                     self.transferred_amount[1 - self.i] - self.locked_amount[self.i] - awit_amount - reserve_amount
        finally: self.lock.release()
        return result

    def test(self):
        print("엥? ", self.deposit[self.i], self.transferred_amount[self.i], self.transferred_amount[1 - self.i],
              self.locked_amount[self.i])

    def fail_payment(self, cr, amount,index):
        if index ==1 :
            i = index - self.i
        else :
            i = self.i

        self.lock.acquire()
        try :
            self.locked_amount[i] -= amount
            self.leaves[i].pop(cr)
        finally: self.lock.release()

    def half_moving_average(self,a,b,c):
        # print("half_moving_average", a,b,c,self.moving_average_capacity[self.i], self.moving_average_capacity[self.i]/2)
        self.moving_average_capacity[self.i] = self.moving_average_capacity[self.i]

    def create_BP(self, w3, cr, initiator, target, secrethash, amount, expiration, s_contract, a_contract, start_time):
        # self.lock.acquire()
        # try:
        #     self.locked_amount[self.i] += amount + s_contract[0]
        # finally:
        #     self.lock.release()
        # print("locked_amount ", self.locked_amount[self.i])

        # uint = 32bytes, address = 20bytes, bytes32 = 32bytes
        leaf = pack_data(['uint256', 'uint256', 'bytes32', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'address'],
                         [amount+s_contract[0], expiration, secrethash, s_contract[0],
                          s_contract[1], a_contract[0][0], a_contract[1][1], start_time, target])
        self.leaves[self.i][cr] = leaf
        temp = []
        for i in list(self.leaves[self.i].values()) :
            temp.append(sha3(i))
        layer = compute_layers(temp)
        tree = MerkleTreeState(layer)
        locksroot = "0x" + merkleroot(tree).hex()
        # print("locksroot ", locksroot)

        self.locksroot[self.i] = locksroot
        self.nonce +=1

        message_data = LockedTransfer_structure(self.nonce, self.chain_id, cr, expiration, self.token_network.address, self.channel_identifier,
                                                 self.addrs[1-self.i], target, initiator, locksroot, secrethash, self.transferred_amount[self.i],
                                                self.locked_amount[self.i], amount, s_contract[0], s_contract[1], a_contract[0][0], a_contract[1][1], start_time)
        packed_message_data = message_data.pack()
        additional_hash = '0x' + sha3(packed_message_data).hex()
        # print("additional_hash ", additional_hash)

        packed_balance = pack_data(['uint256', 'uint256', 'bytes32'], [self.transferred_amount[self.i], self.locked_amount[self.i], locksroot])
        balance_hash = '0x' + sha3(packed_balance).hex()
        # print("balance_hash ", balance_hash)

        packed_balance_proof = pack_data(['uint256', 'bytes32', 'uint256', 'bytes32'],
                                         [self.channel_identifier, balance_hash, self.nonce, additional_hash])

        hashBP = '0x' + sha3(packed_balance_proof).hex()
        signature = w3.eth.account.signHash(message_hash=hashBP, private_key=self.sk)
        # print("signature", signature)
        BP = balanceProof(message_data, additional_hash, balance_hash, signature['signature'].hex())
        self.BP[self.i] = BP

        return BP

    def unlock(self, w3, cr, secret, endTime, aux_incentive, aux_delay, node,initiator):
        BP = self.BP[self.i]
        # remove
        leaf = self.leaves[self.i].pop(cr)
        # print("leaf : ", leaf)
        # print("type : ", type(leaf))
        locked_amount = w3.toInt(leaf[0:32])
        expiration = w3.toInt(leaf[32:64])
        secrethash = (leaf[64:96])
        selected_incentive = w3.toInt(leaf[96:128])
        selected_delay = w3.toInt(leaf[128:160])
        # aux_incentive = w3.toInt(leaf[160:192])
        # aux_delay = w3.toInt(leaf[192:224])
        startTime = w3.toInt(leaf[224:256])

        assert (sha3(secret) == secrethash)

        final_delay = (endTime-startTime) / time_meaningful_constant
        # print("final delay :", final_delay)
        # print("selected_delay", selected_delay/ contract_meaningful_delay_constant)
        # print("aux_delay", aux_delay/ contract_meaningful_delay_constant)
        # print("selected_incentive", selected_incentive)
        # print("aux_incentive", aux_incentive)

        final_incentive = 0
        # selected_incentive = int(round(selected_incentive / contract_meaningful_incentive_constant))
        # selected_delay = int(round(selected_delay
        # aux_incentive = int(round(aux_incentive / contract_meaningful_incentive_constant))
        # aux_delay = aux_delay / contract_meaningful_delay_constant
        #
        contracts = [(selected_incentive, selected_delay / contract_meaningful_delay_constant)]
        for i in range(len(aux_incentive)) :
            temp = aux_incentive[i], (aux_delay[i] / contract_meaningful_delay_constant)
            contracts.append(temp)
        # print("contract", contracts)
        # if node == initiator:
        count = 0
        weight = contract_meaningful_delay_constant / payGo_contract_meaningful_delay_constant
        for contract in contracts:
            if contract[1] >= final_delay / weight:
                final_incentive = contract[0]
                break
            count +=1
        # print("incentive over contracts ,", contracts)
        # print("final_delay : ", final_delay)
        # print("final_incentive : ", final_incentive)

        self.lock.acquire()
        try :
            # print("locked_amount : ", locked_amount)
            # print("selected_incentive : ", selected_incentive)
            # print("final_incentive : ", final_incentive)

            self.locked_amount[self.i] -= locked_amount
            result = locked_amount - selected_incentive + final_incentive
            self.transferred_amount[self.i] += result

            # if selected_incentive < final_incentive :
            #     print("wow~, ", selected_incentive, final_incentive)
        finally:
            self.lock.release()
        # print("locked_amount : ", self.locked_amount[self.i])
        # print("transferred_amount : ", self.transferred_amount[self.i])

        if len(self.leaves[self.i]) != 0 :
            temp = []
            for i in list(self.leaves[self.i].values()):
                temp.append(sha3(i))
            layer = compute_layers(temp)
            tree = MerkleTreeState(layer)
            locksroot = "0x" + merkleroot(tree).hex()
        else :
            locksroot = pack_data(['uint256'], [0])
        # print("locksroot ", locksroot)

        self.locksroot[self.i] = locksroot
        self.nonce += 1

        message_data = unlockTransfer(self.nonce, cr, self.channel_identifier, secret, locksroot,
                                                self.transferred_amount[self.i], self.locked_amount[self.i], locked_amount, result)
        packed_message_data = message_data.pack()
        additional_hash = '0x' + sha3(packed_message_data).hex()
        # print("additional_hash ", additional_hash)

        packed_balance = pack_data(['uint256', 'uint256', 'bytes32'],
                                   [self.transferred_amount[self.i], self.locked_amount[self.i], locksroot])
        balance_hash = '0x' + sha3(packed_balance).hex()
        # print("balance_hash ", balance_hash)

        packed_balance_proof = pack_data(['uint256', 'bytes32', 'uint256', 'bytes32'],
                                         [self.channel_identifier, balance_hash, self.nonce, additional_hash])

        hashBP = '0x' + sha3(packed_balance_proof).hex()
        signature = w3.eth.account.signHash(message_hash=hashBP, private_key=self.sk)
        # print("signature", signature)
        BP = balanceProof(message_data, additional_hash, balance_hash, signature['signature'].hex())
        self.BP[self.i] = BP

        return BP, result, final_incentive, final_delay, count

    def locked_BP(self, BP):
        self.lock.acquire()
        try:
            self.BP[1 - self.i] = BP
            self.locked_amount[1-self.i] += BP.message_data.amount + BP.message_data.selected_incentive
            self.locksroot[1-self.i] = BP.message_data.locksroot
        finally:
            self.lock.release()
        cr = BP.message_data.payment_identifier
        locked_amount = BP.message_data.amount + BP.message_data.selected_incentive
        expiration = BP.message_data.expiration
        secrethash = BP.message_data.secrethash
        selected_incentive = BP.message_data.selected_incentive
        selected_delay = BP.message_data.selected_delay
        aux_incentive = BP.message_data.aux_incentive
        aux_delay = BP.message_data.aux_delay
        startTime = BP.message_data.start_time
        target = BP.message_data.target

        leaf = pack_data(
            ['uint256', 'uint256', 'bytes32', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'address'],
            [locked_amount, expiration, secrethash, selected_incentive,selected_delay, aux_incentive, aux_delay, startTime, target])
        self.leaves[1-self.i][cr] = leaf

        # return self.transferred_amount[1-self.i], self.locked_amount[1-self.i], self.locksroot[1-self.i]
        return locked_amount, selected_delay, startTime

    def unlock_BP(self, BP):
        self.lock.acquire()
        try:
            self.BP[1 - self.i] = BP
            self.transferred_amount[1 - self.i] += BP.message_data.final_amount
            self.locked_amount[1 - self.i] -= BP.message_data.amount
            self.locksroot[1 - self.i] = BP.message_data.locksroot
            self.leaves[1 - self.i].pop(BP.message_data.payment_identifier)
        finally:
            self.lock.release()
        return BP.message_data.transferred_amount, self.locked_amount[1 - self.i], self.locksroot[1 - self.i]

    def get_partner_BP(self):
        return self.BP[1 - self.i]

    def get_state(self):
        return self.transferred_amount[self.i], self.locked_amount[self.i], self.locksroot[self.i]

    def get_partner_state(self):
        return self.transferred_amount[1-self.i], self.locked_amount[1-self.i], self.locksroot[1-self.i]

    def get_partner_leaves(self):
        leaves = list(self.leaves[1-self.i].values())
        types = ["bytes" for _ in leaves]

        return pack_data(types, leaves)
