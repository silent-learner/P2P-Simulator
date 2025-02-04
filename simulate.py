import random
from Peer import *
from utils import *
from Transaction import *
from Graph_utils import *
from Block import *
import simpy as sp

n_peers = 10
z0 = 1
z1 = 0
Ttx = 0.5
IaT = 0.5

# create a peer to peer network
# define which nodes are slow/fast
# and define which nodes are low/high cpu
P2P_network = P2P_network_generate(n_peers, z0, z1)
peers = Peer.peers

# printing peer information
for peer in peers:
    print(peer)

# give some initial balance to everyone
# each peer keeps track of every other peers balance
balances = [random.randint(10, 25) for i in range(n_peers)]
Peer.initial_balances = balances.copy()
for peer in peers:
    peer.everyones_balance = balances.copy()

# create the simpy environment
env = sp.Environment()

# peers will now generate transactions randomly
for peer in peers:
    # filtered_peer = every peer other than itself
    filtered_peer = [x for x in peers if x != peer]

    def transaction_generator_for_every_peer(env, peer, filtered_peer):
        while True:
            waitTime = random.expovariate(1 / Ttx)
            yield env.timeout(waitTime)
            generate_transaction(env, peer, random.choice(filtered_peer), P2P_network)

    env.process(transaction_generator_for_every_peer(env, peer, filtered_peer))


# peers will now try to mine blocks randomly
for peer in peers:

    def block_generator_for_every_peer(env, peer: Peer):
        while True:
            interarrival_block_time = random.expovariate(1 / IaT)
            yield env.timeout(interarrival_block_time)
            yield env.process(generate_block(env, peer, IaT, P2P_network))

    env.process(block_generator_for_every_peer(env, peer))

# run the simulation until some time
env.run(until=100)

for peer in peers:
    make_blockChainTree(
        peer.ledger, 0, f"./BlockChainTrees/Block Chain Tree {peer.ID}.png"
    )

print("-------------------------------The end---------------------------------------")
