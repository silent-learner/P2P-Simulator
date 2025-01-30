import random
from Peer import *
from Graph_utils import *
import simpy as sp

n_peers = 25
z0 = 0.2
z1 = 0.2
Ttx = 10

P2P_network , peers = P2P_network_generate(n_peers)

env = sp.Environment()




print("The end")
