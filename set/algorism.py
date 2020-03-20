from scipy import optimize
import math, time
from settingParameter import contract_meaningful_incentive_constant, contract_meaningful_delay_constant

# contract theory Parameter
Theta = 40
# Omega = 3
# Omega_prime = 4
x0 = [0.1]          # init
bnds = [(0.0,10.0)] # bound

# RTT control Parameter
class RTT :
    def __init__(self):
        self.accumulate_RTT = 0.003
        self.weight = 0.6

    def update_PTT(self, name, newRTT):
        self.accumulate_RTT = self.accumulate_RTT * self.weight + newRTT * (1-self.weight)
        # self.previous_RTT = newRTT
        # print("accumulate_time update between {} : {}".format(name, self.accumulate_RTT))

    def get_accumulate_time(self):
        return self.accumulate_RTT

    def having_accumulate_RTT(self):
        # self.accumulate_RTT = self.accumulate_RTT * self.weight + 0.03 * (1 - self.weight)
        self.accumulate_RTT = self.accumulate_RTT / 2

def sigma(K, N, value):
    return sum(value[n] for n in range(K, N))

def positive_number(x) :
    return x if x > 0 else None

class contract_bundle :
    def __init__(self, account):
        self.creator = account
        self.Incentive = [0]
        self.Client_U = 0     # total client Utility
        self.Client_U_I = [0]
        self.Hub_U = [0]
        self.Hub_type_U = {}
        self.Delay = [0]
        self.Delay_Inverse = [0]
        self.Delta = [0]        # delay addition function
        self.Theta = []
        self.P = []
        self.Omega = 0          # Incentive wegiht parameter for client
        self.Minus = -1
        self.N = 0              # total Theta number
        self.Omega_prime = 0    # unit resource cost for hub nodes

        # self.set_Theta_number(Theta)


    def set_Theta_number(self, n, Omega, Omega_prime):
        self.set_Omega(Omega)
        self.set_Omega_prime(Omega_prime)
        # self.N = n
        # self.Theta = [i for i in range(n+1)]
        # self.P = [1/n for _ in range(n+1)]
        self.N = len(n)-1
        self.Theta = [i for i in n.keys()]
        self.P = [n[i] for i in n.keys()]


    def set_Omega(self, Omega):
        self.Omega = Omega

        # self.print_Omega()

    def set_Omega_prime(self, Omega_prime):
        self.Omega_prime = Omega_prime

        # self.print_Omega_prime()

    def print_N(self):
        print("{}'s N value : {}".format(self.creator, self.N))

    def print_Theta(self):
        print("{}'s Theta value : {}".format(self.creator, self.Theta))

    def print_P(self):
        print("{}'s P value : {}".format(self.creator, self.P))

    def print_Omega(self):
        print("{}'s Omega value :       {}".format(self.creator, self.Omega))

    def print_Omega_prime(self):
        print("{}'s Omega_prime value : {}".format(self.creator, self.Omega_prime))

    def state_print(self, name, value):
        for i in range(len(value)):
            print("{}'s {} index {} : {}".format(self.creator, i, name, value[i]))

    def set_client_utility_i(self, i):
        def optimizeQ(x):
            current_P = self.P[i]
            V_theta_q = self.Theta[i] * math.log(1 + x)
            P_sigma = sigma(i + 1, self.N + 1, self.P)
            if i != self.N:
                Lambda = self.Theta[i] * math.log(1 + x) - self.Theta[i + 1] * math.log(1 + x)
            else:
                Lambda = 0

            return (self.Minus * ((current_P / self.Omega_prime * V_theta_q) +
                             (Lambda / self.Omega_prime * P_sigma) -
                             (current_P * self.Omega * x)))

        return optimizeQ

    def set_Delta(self):
        for k in range(1, self.N+1):
            if k == 1:
                self.Delta.append(0)
            else:
                self.Delta.append(self.Theta[k] * (math.log(1 + self.Incentive[k]) - math.log(1 + self.Incentive[k - 1])))

    def set_delay(self, i):
        delay = (self.Theta[1] * math.log(1 + self.Incentive[1]) + sigma(1, i + 1, self.Delta)) / self.Omega_prime
        self.Delay_Inverse.append(delay)
        if delay != 0:
            delay = 1 / delay
        return (delay)

    def set_client_Utility(self):
        return sum(self.P[i] * (self.Delay_Inverse[i] - self.Omega * self.Incentive[i]) for i in range(1, self.N + 1))

    def set_hub_Utility(self):
        for i in range (1, self.N+1) :
            self.Hub_U.append(self.Theta[i] * math.log(1 + self.Incentive[i]) - self.Omega_prime * self.Delay_Inverse[i])

    def set_hub_type_Utility(self):
        for i in range (1, self.N+1) :
            self.Hub_type_U[self.Theta[i]] = []
            for j in range (1, self.N+1) :
                self.Hub_type_U[self.Theta[i]].append(self.Theta[i] * math.log(1 + self.Incentive[j]) - self.Omega_prime * self.Delay_Inverse[j])

    def check_infeasible(self):
        st,dt = 0,0
        for i in range(len(self.Incentive)-1) :
            if self.Incentive[i] > self.Incentive[i + 1] :
                st = i+1

                for j in range(st + 1, len(self.Incentive)):
                    if self.Incentive[st - 1] < self.Incentive[j]:
                        dt = j - 1
                        break
                    else :
                        dt = len(self.Incentive)-1

        return {'st' : st, 'dt' : dt}

    def execute(self, contract_theta, Omega, Omega_prime, x0=x0,bnds=bnds):
        self.set_Theta_number(contract_theta, Omega, Omega_prime)

        # 1_ for
        for i in range(1, self.N+1) :
            temp = self.set_client_utility_i(i)
            result = optimize.minimize(temp, x0, method="TNC", bounds=bnds, options={'maxiter': 1000})
            # print("result.fun", result.fun)
            # print("result.x bool", result.x)
            self.Client_U_I.append(result.fun)
            self.Incentive.append(result.x)
        # print("result len", len(result.x))
        # self.state_print("incentive", self.Incentive)
        self.set_Delta()


        count = 0
        while True:
            infeasible_point = self.check_infeasible()
            if infeasible_point['st'] == 0: break
            # print("infeasible_start_point : {} ".format(infeasible_point['st']))
            # print("infeasible_end_point : {} ".format(infeasible_point['dt']))
            # print()
            count += 1
            # self.state_print("client utility", self.Client_U_I)
            # self.state_print("incentive", self.Incentive)

            # print("================={} not feasible=================".format(count))

            for i in range(infeasible_point['st'], infeasible_point['dt'] + 1):
                # temp = self.set_client_infeasible_utility_i(infeasible_point['st']-1, infeasible_point['dt'])
                # result = optimize.minimize(temp, x0, method="TNC", bounds=bnds, options={'maxiter': 1000})

                # print("Client_U_I {} index {} -> {} ".format(i, self.Client_U_I[i],
                #                                              self.Client_U_I[infeasible_point['st'] - 1]))
                # print("Incentive {} index {} -> {} ".format(i, self.Incentive[i],
                #                                             self.Incentive[infeasible_point['st'] - 1]))
                self.Client_U_I[i] = self.Client_U_I[infeasible_point['st'] - 1]
                self.Incentive[i] = self.Incentive[infeasible_point['st'] - 1]



        #2_ for
        for i in range(1, self.N+1) :
            self.Delay.append(self.set_delay(i))

        # self.state_print("Delaay", self.Delay)
        self.set_hub_type_Utility()

        # for i in range(len(self.Incentive)) :
            # if self.Incentive[0] == 0 :
            #     self.Incentive.pop(0)
            #     self.Delay.pop(0)

        bundle = {"Incentive" : self.Incentive, "Delay" : self.Delay}
        bundle = self.Xcontract_meaningful_costant(bundle)
        # bundle = self.linearation(bundle)
        return bundle

    def Xcontract_meaningful_costant(self, bundle):
        length = len(bundle["Incentive"])
        for i in bundle.keys():
            k = 0
            for j in range(length):
                if bundle[i][k] == 0:
                    bundle[i].pop(k)
                elif bundle[i][k] >= 1.5 and i == "Delay" :
                    # print("pop", bundle[i][k])
                    bundle[i].pop(k)
                else :
                    if i == "Incentive" :
                        bundle[i][k] = bundle[i][k] * contract_meaningful_incentive_constant
                    else :
                        bundle[i][k] = bundle[i][k] * contract_meaningful_delay_constant
                    k +=1
        return bundle

    def get_producer_utility(self, incetive, delay , Omega):
        delay = 1 / (delay)
        utility = delay - Omega * incetive
        return utility

    def linearation(self, bundle):
        top = len(bundle["Delay"]) -1

        x1 = bundle["Incentive"][0]
        x2 = bundle["Incentive"][top]
        y1 = bundle["Delay"][0]
        y2 = bundle["Delay"][top]

        a =  (y1 - y2) / (x1-x2)
        b = y1 - (a * x1)
        for i in range(len(bundle["Incentive"])):
            bundle["Incentive"][i] = (bundle["Delay"][i] - b) / a

        return bundle

# test = {}
# A_model = []
# for i in range(40) :
#     if i < 39 :
#         A_model.append(1)
#     else :
#         A_model.append(1)
#
# for i in range(40) :
#     test[i]  = A_model[i]
# start = time.time()
# a = contract_bundle("asd").execute(test,1, 3.5)
# end = time.time()
# print(end-start)
# # print("len", (a["Delay"]))
# print(a)
# temp_d = []
# temp_i = []
# for i in range(len(a["Delay"])) :
#     temp_d.append(a["Delay"][i]/25)
#     temp_i.append(a["Incentive"][i][0]/100)
# print(temp_d)
# print(temp_i)
# for i in range(len(a["Incentive"])) :
#     incentive = a["Incentive"][i] / contract_meaningful_incentive_constant
#     delay = a["Delay"][i] / contract_meaningful_delay_constant
#     test =contract_bundle("asd").get_producer_utility(incentive, delay, 2)
#     print(test)
