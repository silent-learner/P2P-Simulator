import random

import networkx as nx

def random_graph(peers):
    P2P_network = nx.Graph()

    for peer in peers:
        P2P_network.add_node(peer.ID)

    for peer in peers:
        degree = random.randint(3,6)
        effective_degree = max(0,degree - len(peer.neighbours))
        candiadtes = []
        for p in peers:
            if p != peer:
                candiadtes.append(p)

        neighbours = random.sample(candiadtes, effective_degree)

        for neigh in neighbours:
            if len(neigh.neighbours) < 6:
                peer.neighbours.add(neigh)
                neigh.neighbours.add(peer)

    for peer in peers:
        print(peer.ID,end='--->')
        for neigh in peer.neighbours:
            print(neigh.ID,end=',')
            P2P_network.add_edge(peer.ID,neigh.ID)
        print()

    return P2P_network
def isConnected(G : nx.Graph):
    return nx.is_connected(G)