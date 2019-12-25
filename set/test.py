
# 변수조정
#: time.sleep 몇초?
#: contract delay 설정
# time.sleep : RTT
# contract delay : x5 [ py - contract_select method ]
# aux_contract = selected contract 아래 계약, 만약 없으면 selected_contract와 같게 설정
# target contract = bundle = {"Incentive" : 0.1, "delay" : 0.2}
# incetive deay * 100 -> contract_meaningful_constant

# 수정
# 1. 반대쪽 채널에서 payment가 안들어오는 경우가 빈번함
# -> expiration time이후에 roll back -> on chain 해결
# -> 악의적으로 행동안해도 on chain 접근하는 경우가 생김


# aux contract 수정 필요

