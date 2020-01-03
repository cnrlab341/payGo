class contractTable :
    def __init__(self, message):
        self.cr = message.cr
        self.initiator = message.initiator
        self.check_propose = []
        self.producer = ""
        self.consumer = ""
        self.target = message.target
        self.amount = message.amount
        self.contract_bundle = {}
        self.receive_contract_bundle = {}
        self.selected_contract = tuple
        self.selected_index = -1
        self.additional_contract = tuple
        self.my_contract = tuple
        self.secret = 0
        self.startTime = 0
        self.endTime = 0
        self.signed_endTime = 0
        self.temp_selected_contract = {}
        self.temp_additional_contract = {}
        self.temp_selected_index = {}
        self.temp_consumer = []
        self.send_selected_contract = []
        self.complete_reject_contract = []
        self.state = ""
        self.selection_direction = 1
        self.payment_startTime = 0
        self.aready_reservation_delay = 0
        self.aux_delay = []
        self.aux_incentive = []
        self.selection_RTT_start = 0
        self.lock_time = [] # 0 : startTime, 1 : endTime
        self.amount_ratio = 0
        self.contract_predict_time = 0

class balanceProof :
    def __init__(self,  message_data, additional_hash, balance_hash, signature):
        self.message_data = message_data
        self.additional_hash = additional_hash
        self.balance_hash = balance_hash
        self.signature = signature


class payer_result :
    def __init__(self):
        self.delay = []
        self.incentive = []
        self.utility = []
        self.zero_incentive = 0
        self.onchain_access = 0
        self.complete_payment = 0
        self.complete_payment_round = []
        self.zero_incentive_delay = {}
        self.contract_delay = []
        self.total_utility = []
        self.protocol_time = {}
        self.pending_payment_settle = {}
        self.select_time = {}
        self.complete = False
        self.pending_queue = {} # initiator, hub1, hub2
        self.pending_queue_lock = {}  # initiator, hub1, hub2
        self.capacity = {} #initiator, hub1, hub2
        self.balance = {} #initiator, hub1, hub2
        self.receive_theta = {} #initiator, hub1, hub2
        self.selected_contract = {}
        self.onchain_access_node = {}
        self.onchain_access_capacity = {}
        self.onchain_access_balance = {}
        self.onchain_access_selected_contract = {}
        self.onchain_access_pendingTime = {}
        self.onchain_access_pendingQueue = {}
        self.payGo_startTime = 0
        self.processing_tx = 0
        self.current_RTT = []
        self.proposal_complete = {}
        self.pending_locked_transfer = {}
        self.payment_endTime = []
        self.contract_boundary = {}
        self.onchain_access_contract_boundary = {}
        self.turningPoint = 0
        self.fail_count = 0

class hub_result :
    def __init__(self):
        self.hub1 = []
        self.hub2 = []
        self.utility = []
        self.incentive = []
        self.zero_incentive = 0
        self.zero_incentive_delay = {}
        self.contract_delay = []
        self.total_utility = []
        self.complete_payment_round = []
        self.complete = False
        self.h1_contract_bundle = []
        self.h2_contract_bundle = []
        self.pending_locked_transfer = {}
