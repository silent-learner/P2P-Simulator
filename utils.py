import networkx as nx
import matplotlib.pyplot as plt
from Peer import *
import random

def delay(A : Peer , B : Peer , m):
        prop_delay = A.prop_delays[B.ID]
        cij = 5000000 if A.isSlow or B.isSlow else 100000000
        trn_delay = (1024*8*m)/cij
        queing_delay = random.expovariate(cij/96000)
        return prop_delay + queing_delay + trn_delay
        

def make_blockChainTree(graph,genesis,filename="tree_multipartite.png"):
    plt.figure(figsize=(10, 6))  

    layers = nx.single_source_shortest_path_length(graph, genesis)
    for node in graph.nodes:
        graph.nodes[node]["subset"] = layers.get(node, 0)

    pos = nx.multipartite_layout(graph, align='horizontal',  subset_key="subset")

    nx.draw(graph, pos, labels={n: n.BlkId for n in graph.nodes}, node_color="lightblue", edge_color="black",
            font_weight="bold", arrows=True)

    plt.savefig(filename, format="png", dpi=300)
    plt.clf()