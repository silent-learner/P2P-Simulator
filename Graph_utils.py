import random
import matplotlib.pyplot as plt
import networkx as nx
from Peer import Peer
from Block import Block


def random_graph():
    P2P_network = nx.Graph()
    peers = Peer.peers
    for peer in peers:
        P2P_network.add_node(peer.ID)

    for peer in peers:
        degree = random.randint(3, 6)
        # making sure that the max_degree never exceeds 6
        effective_degree = max(0, degree - P2P_network.degree(peer.ID))
        candidates = []
        for p in peers:
            if (
                p != peer
                and P2P_network.degree(p.ID) < 6
                and not P2P_network.has_edge(peer.ID, p.ID)
            ):
                candidates.append(p)

        neighbours = random.sample(candidates, min(len(candidates), effective_degree))
        for p in neighbours:
            # pick a minimum positive value pij
            # for propagation delay from uniform(10 ms to 500 ms)
            # pij is stored in seconds
            P2P_network.add_edge(
                peer.ID, p.ID, pij=random.uniform(10 / 1000, 500 / 1000)
            )

    return P2P_network


def P2P_network_generate(n_peers, z0, z1):
    genesis_block = Block()
    for i in range(n_peers):
        Peer(i, genesis=genesis_block)
    peers = Peer.peers

    # slow peers
    slow = z0 * n_peers
    slow_hashing_power = 1 / (n_peers * (10 - 9 * z1))
    slow_peers = random.sample(peers, int(slow))

    for peer in slow_peers:
        peer.isSlow = True

    for peer in peers:
        if peer.isSlow:
            peer.hashingPower = slow_hashing_power
        else:
            peer.hashingPower = 10 * slow_hashing_power

    # normalizing hashing_power
    total_hashing_power = sum(p.hashingPower for p in peers)
    for peer in peers:
        peer.hashingPower = peer.hashingPower / total_hashing_power

    # lowcpu peers
    lowcpu = z1 * n_peers
    lowcpu_peers = random.sample(peers, int(lowcpu))
    for peer in lowcpu_peers:
        peer.isLowCPU = True

    # creating the network graph
    P2P_network = random_graph()

    # making sure that the graph is connected
    # and that the min_degree >= 3
    while (
        not nx.is_connected(P2P_network) or min(dict(P2P_network.degree()).values()) < 3
    ):
        P2P_network = random_graph()

    nx.draw(P2P_network, with_labels=True)
    plt.savefig("P2P_network.png")
    plt.clf()

    return P2P_network
