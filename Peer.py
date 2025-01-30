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
        self.process = env.process(self.generate_transactions())

    def generate_transactions(self):
        while True:
            interarrival_time = random.exponential(1 / self.tx_rate)  # Exponential delay
            yield self.env.timeout(interarrival_time)  # Wait for the next transaction
            self.tx_count += 1
            print(f'Time {self.env.now:.2f}: Node {self.node_id} generated Transaction {self.tx_count}')

    def __str__(self):
        return f'Peer Id {self.ID} neighbours : {self.neighbours} isslow : {self.isSlow} isHighCPu : {self.isLowCPU} balance : {self.balance}'

