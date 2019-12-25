# signature V를 생성하기 위해 사용
# protect to replay attack
chain_id = 1337

# block count
settlement_timeout_min = 10
settlement_timeout_max = 100
max_token_networks = 10

# Token network Parameter
channel_participant_deposit_limit = 1000
token_network_deposit_limit = 100000

# setting
node_count = 30          # 30개까지 가능
mint_ERC20 = 1000000000  # smart contract의 TOKEN 총량, node count에 맞게 분배
# distribute_ERC20 = 250  # 노드당 전송할 토큰양
# initial_deposit = [100 for _ in range(node_count)] # deposit
on_chain_access_cost = 100000
alpha = 50
theta = 40


contract_meaningful_incentive_constant = 100
contract_meaningful_delay_constant = 1000
time_meaningful_constant = 1000




