import random
from Peer import *
from utils import *
from Transaction import *
from Graph_utils import *
import simpy as sp

n_peers = 8
z0 = 0.2
z1 = 0.2
Ttx = 0.1
IaT = 600

P2P_network , peers = P2P_network_generate(n_peers, z0, z1)

env = sp.Environment()

transactions = []

def generate_transaction(env, sender : Peer, receiver : Peer): 
    txn = Transaction(env.now,sender,receiver,random.randint(1,15))
    print(txn)
    if sender.balance < txn.amount:
        sender.mempool.append(txn)
        txn.peers_already_received.add(sender.ID)
        print(f"Txn {txn.TxnID} created by {sender.ID} and added in its mempool at {env.now}.")
        for neigh in sender.neighbours:
            if neigh not in txn.peers_already_received:
                env.process(forward_transaction(env,txn,sender,neigh))


def forward_transaction(env,txn : Transaction,peer1 : Peer,peer2 : Peer):
    latency =  delay(peer1,peer2,1)
    yield env.timeout(latency)

    if txn.TxnID in [trxn.TxnID for trxn in peer2.mempool]:
        return
    peer2.mempool.append(txn)
    print(f"Txn {txn.TxnID} reached peer {peer2.ID} and added to its mempool at time {env.now}.")
    txn.peers_already_received.add(peer2.ID)
    for neigh in peer2.neighbours:
        if neigh != peer1 and neigh not in txn.peers_already_received:
            env.process(forward_transaction(env,txn,peer2,neigh))


def process_transaction(env):
    pass


def generate_block(env,peer :Peer):
    txns = peer.mempool
    block = Block(peer,env.now,)

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

for peer in peers:

    def block_generator_for_every_peer(env,peer : Peer):
        while True:
            generate_block(env, peer)
            interarrival_blovk_time = random.expovariate(peer.hashingPower/IaT)
            yield env.timeout(interarrival_blovk_time)

    env.process(block_generator_for_every_peer(env,peer))


# for peer in peers:
#     print(peer.ID)
#     for key , value in peer.prop_delays.items():
#         print('\t',key,value)

env.run(until=5)



for peer in peers:
    print(peer.ID,peer.isSlow,peer.hashingPower)
    # for txn in peer.mempool:
    #     print('\t',txn)
    print()


print("------------------------------------The end--------------------------------------------")
