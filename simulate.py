import random
import networkx as nx
from Peer import *
from Graph_utils import *
import matplotlib.pyplot as plt
import simpy as sp

n_peers = 25
z0 = 0.2
z1 = 0.2
Ttx = 10

def P2P_network_generate(n_peers):

    peers = [Peer(i + 1) for i in range(n_peers)]

    slow = z0 * n_peers
    lowcpu = z1 * n_peers

    slow_peers = random.sample(peers, int(slow))
    lowcpu_peers = random.sample(peers, int(lowcpu))

    for peer in slow_peers:
        peer.isSlow = True

    for peer in lowcpu_peers:
        peer.isLowCPU = True

    P2P_network = random_graph(peers)

    min_degree = min([degree for _ , degree in P2P_network.degree()])
    print("Min degree", min_degree)
    max_degree = max([degree for _ , degree in P2P_network.degree()])
    print("Max degree", max_degree)
    while (not isConnected(P2P_network)) or min_degree < 3:
        P2P_network = random_graph(peers)
        min_degree = min([degree for _, degree in P2P_network.degree()])
        print("Min degree", min_degree)
        max_degree = max([degree for _ , degree in P2P_network.degree()])
        print("Max degree", max_degree)

    nx.draw(P2P_network, with_labels=True)
    plt.savefig('P2P_network.png')
    plt.clf()

    return P2P_network,peers

P2P_network , peers = P2P_network_generate(n_peers)

env = sp.Environment()




print("The end")
