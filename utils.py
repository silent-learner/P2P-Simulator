import networkx as nx
import matplotlib.pyplot as plt
from Peer import *
import random


# Peer_A is the sender
# Peer_B is the receiver
# m is size of the message in KB
def delay(A: Peer, B: Peer, m, P2P_network):
    return 10
    # prop_delay is measured in seconds
    prop_delay = P2P_network[A.ID][B.ID]["pij"]

    # 100 Mbps if both are fast
    # else 5Mbps
    # cij is the speed of network in bits/second
    cij = 5000000 if A.isSlow or B.isSlow else 100000000

    # trn_delay is measured in seconds
    trn_delay = (1024 * 8 * m) / cij
    queing_delay = random.expovariate(cij / 96000)
    return prop_delay + queing_delay + trn_delay


def make_blockChainTree(graph, genesisID, filename="tree_multipartite.png"):
    plt.figure(figsize=(10, 6))

    layers = nx.single_source_shortest_path_length(graph, genesisID)
    for node in graph.nodes:
        graph.nodes[node]["subset"] = layers.get(node, 0)

    pos = nx.multipartite_layout(graph, align="vertical", subset_key="subset")

    nx.draw(
        graph,
        pos,
        labels={n: n for n in graph.nodes},
        node_color="lightblue",
        edge_color="black",
        font_weight="bold",
        arrows=True,
        node_size=50,
    )

    plt.savefig(filename, format="png", dpi=300)
    plt.clf()


def print_nx_tree(graph, node=0, prefix="", f=""):
    children = list(graph.successors(node))
    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        connector = "└── " if is_last else "├── "
        f.write(prefix + connector + str(child) + "\n")
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_nx_tree(graph=graph, node=child, prefix=new_prefix, f=f)
