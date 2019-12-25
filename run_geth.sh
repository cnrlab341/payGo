# genesis.json file register
# geth --datadir ./gethchain init ./genesis.json console

#geth attach ipc:./gethchain/geth.ipc

# geth mining start
#geth --dev --dev.period 2 --datadir ./gethchain --rpc --rpccorsdomain '*' --rpcport 8646 --rpcapi "eth,net,web3,debug" --port 32323 --maxpeers 0 --targetgaslimit 994712388 console

# mining x
#geth --dev.period 2 --datadir ./gethchain --rpc --rpccorsdomain '*' --rpcport 8646 --rpcapi "eth,net,web3,debug" --port 32323 --maxpeers 0 --targetgaslimit 994712388 console
