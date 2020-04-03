# payGo : Incentive Comparable Payment Routingbased on Contract theory

Payment Channel Networks (PCN) emerges as a most promising offchain solution for the crypto-currencies which offloads transactions from the blockchain and handles them directly using a payment channel with minimum involvement of the blockchain. A routing protocol  for the PCN is critical to find a Path-Based Transaction (PBT) path with low latency and high throughput and several routing protocols  have been proposed for issues of decentralization, concurrency and privacy. However, an incentive mechanism for the Payment Service Provider (PSP) has not been sufficiently studied, which is a key to a successful  PBT.  

PayGo routing protocol not only discovers a feasible path, but derives optimal incentive for the PSPs using contract theory. Furthermore, the payGo makes the PSP have a contract with a counterparty to grantee payment latency and throughput with penalty. We implement the payGo protocol extending Raiden network. 

This git repo provides a implementation of PCN. and (simulation.py) implements a P2P topology.  

<img src="https://user-images.githubusercontent.com/35050199/78328119-572a2200-75b9-11ea-8060-431963dd0821.png" width="30%"></img>

# Contents

<ul>
  <li>algorithm.py : implementation the contract theory</li>
  <li>contract.py : interconnecting with blockchain</li>
  <li>key.py : account for blockchain</li>
  <li>channelState.py : state of the two nodes participating in the payemnt channel</li>
  <li>message.py : PayGo message structure</li>
  <li>node.py : </li>
  <li>settingParameter.py : </li>
  <li>structure.py</li>
</ul>





