from raiden.transfer.state import HashTimeLockState
from raiden.constants import UINT256_MAX
from raiden.encoding import messages
from raiden.utils.signing import pack_data
from raiden.utils.typing import (
    Address,
    BlockExpiration,
    ChainID,
    ChannelID,
    Locksroot,
    MessageID,
    Optional,
    PaymentID,
    Secret,
    SecretHash,
    TokenAmount,
    TokenNetworkAddress,
    BlockExpiration,
    SecretHash,
)

class fail :
    def __init__(self, content):
        self.id = "fail"
        self.content = content

class contractPropose :
    def __init__(self, cr, initiator, sender, recipient, target, amount, contract_bundle):
        self.id = "contractPropose"
        self.cr = cr
        self.initiator = initiator
        self.producer = sender
        self.consumer = recipient
        self.target = target
        self.amount = amount
        self.contract_bundle = contract_bundle

class initContractPropose :
    def __init__(self, initiator, recipient, target, amount, secret, channel_probability):
        self.id = "initContractPropose"
        self.initiator = initiator
        self.recipient = recipient
        self.target = target
        self.amount = amount
        self.secret = secret
        self.channel_probability = channel_probability

class endcontractPropose :
    def __init__(self):
        self.id = "endcontractPropose"

class contractSelect :
    def __init__(self, cr, initiator, sender, recipient, target, incentive, delay, selected_index, additional_incentive, additional_delay, propose_endTime):
        self.id = "contractSelect"
        self.cr = cr
        self.initiator = initiator
        self.producer = recipient
        self.consumer = sender
        self.target = target
        self.incentive = incentive
        self.delay = delay
        self.selected_index = selected_index
        self.additional_incentive = additional_incentive
        self.additional_delay = additional_delay
        self.path = []
        self.propose_endTime = propose_endTime

class contractConfirm :
    def __init__(self, cr, producer, consumer, incentive, delay):
        self.id = "contractConfirm"
        self.cr = cr
        self.producer = producer
        self.consumer = consumer
        self.incentive =incentive
        self.delay = delay


class contractReject :
    def __init__(self, cr, requester, parnter, type):
        self.id = "contractReject"
        self.type = type
        self.cr = cr
        self.requester = requester
        self.parnter = parnter

class LockedTransfer_structure :
    cmdid = messages.LOCKEDTRANSFER
    def __init__(
            self,
            nonce: int,
            chain_id: ChainID,
            payment_identifier,
            expiration : BlockExpiration, ##
            token_network_address: Address,
            channel_identifier: ChannelID,
            recipient: Address,
            target: Address,
            initiator: Address,
            locksroot: Locksroot,
            secrethash : SecretHash,      ##
            transferred_amount: TokenAmount,
            locked_amount: TokenAmount,
            amount : int,                 ##
            selected_incentive : int,
            selected_delay : int,
            aux_incentive: int,
            aux_delay: int,
            start_time: int,
    ):
        self.nonce = nonce
        self.chain_id = chain_id
        self.payment_identifier = payment_identifier
        self.expiration = expiration
        self.token_network_address = token_network_address
        self.channel_identifier = channel_identifier
        self.recipient = recipient
        self.target = target
        self.initiator = initiator
        self.locksroot = locksroot
        self.secrethash = secrethash
        self.transferred_amount = transferred_amount
        self.locked_amount = locked_amount
        self.amount = amount
        self.selected_incentive = selected_incentive
        self.selected_delay = selected_delay
        self.aux_incentive = aux_incentive
        self.aux_delay = aux_delay
        self.start_time = start_time

    def pack(self):
        return pack_data([
            'uint8', 'uint64', 'uint256', 'bytes32', 'uint256',
            'address', 'uint256', 'address', 'address', 'address',
            'bytes32', 'bytes32', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256',
        ], [
            self.cmdid, self.nonce, self.chain_id, self.payment_identifier, self.expiration,
            self.token_network_address,self.channel_identifier, self.recipient, self.target, self.initiator,
            self.locksroot, self.secrethash, self.transferred_amount, self.locked_amount, self.amount, self.start_time,
            self.selected_incentive, self.selected_delay, self.aux_incentive, self.aux_delay,
        ])
class unlockTransfer :
    def __init__(
            self,
            nonce: int,
            payment_identifier,
            channel_identifier: ChannelID,
            secret : Secret,      ##
            locksroot: Locksroot,
            transferred_amount: TokenAmount,
            locked_amount: TokenAmount,
            amount = int,
            final_amount = int,
    ):
        self.id = "unlockTransfer"
        self.nonce = nonce
        self.payment_identifier = payment_identifier
        self.channel_identifier = channel_identifier
        self.secret = secret
        self.locksroot = locksroot
        self.transferred_amount = transferred_amount
        self.locked_amount = locked_amount
        self.amount = amount
        self.final_amount = final_amount


    def pack(self):
        return pack_data([
            'uint64', 'bytes32','uint256', 'bytes32', 'bytes32',  'uint256', 'uint256',
        ], [
            self.nonce, self.payment_identifier, self.channel_identifier, self.secret,
            self.locksroot,  self.transferred_amount, self.locked_amount,
        ])

class LockedTransfer :
    def __init__(self, cr, sender, recipient, BP, target, initiator, selected_contract, aux_contract) :
        self.id = "lockedTransfer"
        self.cr = cr
        self.producer = sender
        self.consumer = recipient
        self.BP = BP
        self.initiator = initiator
        self.target = target
        self.selected_contract = selected_contract
        self.aux_contract = aux_contract



class sendSecret :
    def __init__(self, cr, secret, initiator, target):
        self.id = 'sendSecret'
        self.cr = cr
        self.secret = secret
        self.initiator = initiator
        self.target = target

class resSecret :
    def __init__(self, cr, initiator, secret):
        self.id = 'resSecret'
        self.cr = cr
        self.initiator = initiator
        self.secret = secret

class revealSecret :
    def __init__(self, cr, secret, endTime, signed_endTime, producer, consumer, locked_transfer_endtime):
        self.id = "revealSecret"
        self.cr = cr
        self.secret = secret
        self.endTime = endTime
        self.signed_endTime = signed_endTime
        self.producer = producer
        self.consumer = consumer
        self.locked_transfer_endtime = locked_transfer_endtime

class resRevealSecret :
    def __init__(self, cr, sender, recipient, BP, finalAmount):
        self.id = "resRevealSecret"
        self.cr = cr
        self.producer = sender
        self.consumer = recipient
        self.BP = BP
        self.finalAmount = finalAmount

class completePayGo :
    def __init__(self, name):
        self.id = "complete"
        self.name = name

class waitContractSelect :
    def __init__(self):
        self.id = "waitContractSelect"

class selectionComplete :
    def __init__(self):
        self.id = "selectionComplete"

class token_network :
    def __init__(self, address):
        self.address = address