import random

import networkx as nx

class Peer:
    def __init__(self,ID,genesis):
        self.ID = ID
        self.prop_delays = {}
        self.isSlow = False
        self.isLowCPU = False
        self.balance = random.randint(10,25)
        self.neighbours = set()
        self.mempool = []
        self.hashingPower = 0
        self.Tree = set()
        self.Tree.add(genesis)
        self.ledger = nx.DiGraph()
        self.genesis = genesis
        self.blocklist = []
        self.ledger.add_node(genesis)
        self.blocklist = [genesis]
        self.everyones_balance = {}


    def __str__(self):
        return f'Peer Id {self.ID} isslow : {self.isSlow} isHighCPU : {self.isLowCPU} balance : {self.balance}'

