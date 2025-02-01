import random
import matplotlib.pyplot as plt
import networkx as nx
from Peer import Peer
from Block import Block


def random_graph(peers):
    P2P_network = nx.Graph()

    # add each peer id as a node in the graph
    for peer in peers:
        P2P_network.add_node(peer.ID)

    for peer in peers:
        # choose a random degree for this peer
        # if random degree is less than the number
        # of current neighbours then try to add more neighbours
        degree = random.randint(3,6)
        effective_degree = max(0,degree - len(peer.neighbours))

        # candidates are the peers that are not connected to the current peer
        candidates = []
        for p in peers:
            if p != peer and p not in peer.neighbours: # p not in neighbours?
                candidates.append(p)

        neighbours = random.sample(candidates, effective_degree)

        for neigh in neighbours:
            if len(neigh.neighbours) < 6:
                peer.neighbours.add(neigh)
                neigh.neighbours.add(peer)

    for peer in peers:
        # print(peer.ID,end='--->')
        for neigh in peer.neighbours:
            # print(neigh.ID,end=',')

            # weight of an edge is pij
            # the positive minimum value (speed of light)
            # chose from a uniform distribution of 10 ms to 500 ms.
            P2P_network.add_edge(peer.ID,neigh.ID,weight=random.uniform(10/1000,500/1000))
        # print()

    return P2P_network

def isConnected(G : nx.Graph):
    return nx.is_connected(G)

def P2P_network_generate(n_peers, z0, z1):
    genesis_block = Block(None,0,None)
    peers = [Peer(i,genesis=genesis_block) for i in range(n_peers)]

    slow = z0 * n_peers
    lowcpu = z1 * n_peers

    slow_peers = random.sample(peers, int(slow))
    lowcpu_peers = random.sample(peers, int(lowcpu))

    # since slow peers hashing power = 1/10 of fast peer hashing power
    # we can calculate slow peer hashing power as follows
    slow_hashing_power = 1/(n_peers*(10-9*z1)) 

    for peer in slow_peers:
        peer.isSlow = True
    
    total_hashing_power = 0
    for peer in peers:
        if peer.isSlow:
            peer.hashingPower = slow_hashing_power
        else:
            peer.hashingPower = 10*slow_hashing_power
        total_hashing_power += peer.hashingPower

    for peer in peers:
        peer.hashingPower = peer.hashingPower/total_hashing_power

    for peer in lowcpu_peers:
        peer.isLowCPU = True

    P2P_network = random_graph(peers)

    min_degree = min([degree for _ , degree in P2P_network.degree()])
    # print("Min degree", min_degree)
    # max_degree = max([degree for _ , degree in P2P_network.degree()])
    # print("Max degree", max_degree)
    while (not isConnected(P2P_network)) or min_degree < 3:
        P2P_network = random_graph(peers)
        min_degree = min([degree for _, degree in P2P_network.degree()])
        # print("Min degree", min_degree)
        # max_degree = max([degree for _ , degree in P2P_network.degree()])
        # print("Max degree", max_degree)


    for (u,v,pij) in P2P_network.edges(data=True):
        # print(u,v,pij,end='--')
        peers[u].prop_delays[v] = pij['weight']
        peers[v].prop_delays[u] = pij['weight']

    nx.draw(P2P_network, with_labels=True)
    plt.savefig('P2P_network.png')
    plt.clf()

    return P2P_network,peers