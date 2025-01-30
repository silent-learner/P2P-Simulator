import random
from Peer import *
from Transaction import *
from Graph_utils import *
import simpy as sp

n_peers = 8
z0 = 0.2
z1 = 0.2
Ttx = 10

P2P_network , peers = P2P_network_generate(n_peers, z0, z1)

env = sp.Environment()

transactions = []

def generate_transaction(env, p1 : Peer, p2 : Peer): 
    txn = Transaction(env.now,p1,p2,random.randint(10,25))
    print(txn)
    p1.mempool.append(txn)


def process_transaction(env):
    pass

for peer in peers:
    # 1. generate first transaction for each peer
    filtered_peer = [x for x in peers if x != peer]
    def transaction_generator_for_every_peer(env, peer, filtered_peer):
        while True:
            waitTime = random.expovariate(1 / Ttx)
            yield env.timeout(waitTime)
            generate_transaction(env, peer, random.choice(filtered_peer))

    env.process(transaction_generator_for_every_peer(env, peer, filtered_peer))
    # 2. whenever a transaction is processed, another transaction is generated



# for peer in peers:
#     print(peer.ID)
#     for key , value in peer.prop_delays.items():
#         print('\t',key,value)



env.run(until=100)
print("------------------------------------The end--------------------------------------------")
