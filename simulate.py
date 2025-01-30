import random
from Peer import *
from Transaction import *
from Graph_utils import *
import simpy as sp

n_peers = 25
z0 = 0.2
z1 = 0.2
Ttx = 10

P2P_network , peers = P2P_network_generate(n_peers, z0, z1)

env = sp.Environment()

transactions = []

def generate_transaction(env, p1 : Peer, p2 : Peer): 
    print(f'{env.now}: Transaction generated: {p1.ID} to {p2.ID}')
    txn = Transaction(env.now,p1,p2,random.randint(10,25))
    p1.mempool.append(txn)
    # transactions.append({"current_time": env.now, "sender": p1, "receiver": p2})

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

env.run(until=100)

print("The end")
