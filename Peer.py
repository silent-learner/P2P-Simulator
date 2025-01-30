import random

import networkx as nx


class Peer(object):
    def __init__(self,ID,env):
        self.env = env
        self.ID = ID
        self.isSlow = False
        self.isLowCPU = False
        self.balance = random.randint(10,25)
        self.neighbours = set()
        self.mempool = []
        self.ledger = nx.Graph()


    def __str__(self):
        return f'Peer Id {self.ID} neighbours : {self.neighbours} isslow : {self.isSlow} isHighCPu : {self.isLowCPU} balance : {self.balance}'

