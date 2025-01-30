import simpy
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class Transaction:
    """Transaction object containing sender, receiver, and unique ID."""
    tx_counter = 0  # Global counter for unique transaction IDs

    def __init__(self, sender, receiver, timestamp):
        self.id = f"Tx-{Transaction.tx_counter}"
        Transaction.tx_counter += 1
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp

    def __repr__(self):
        return f"{self.id}({self.sender.node_id} → {self.receiver.node_id})"

class Node:
    """Represents a peer in the network."""
    
    def __init__(self, env, node_id, tx_rate, block_rate, all_nodes):
        self.env = env
        self.node_id = node_id
        self.tx_rate = tx_rate
        self.block_rate = block_rate  # Block generation rate
        self.all_nodes = all_nodes  # Reference to all nodes for transactions
        self.received_transactions = set()  # Store transactions to include in blocks
        self.process = env.process(self.generate_transactions())  # Start transaction generation
        self.block_process = env.process(self.generate_blocks())  # Start block creation

    def generate_transactions(self):
        """Generate transactions at exponential intervals and broadcast them."""
        while True:
            yield self.env.timeout(np.random.exponential(1 / self.tx_rate))  # Wait for next transaction
            
            # Choose a random receiver (excluding self)
            receiver = random.choice([n for n in self.all_nodes if n != self])
            
            # Create a new transaction
            tx = Transaction(sender=self, receiver=receiver, timestamp=self.env.now)
            
            print(f"Time {self.env.now:.2f}: Node {self.node_id} created and broadcasting {tx}")
            self.broadcast_transaction(tx)

    def broadcast_transaction(self, tx):
        """Broadcast transaction to all nodes except the sender."""
        for node in self.all_nodes:
            if node != self:
                node.receive_transaction(tx)

    def receive_transaction(self, tx):
        """Receive a transaction and store it if not already seen."""
        if tx not in self.received_transactions:
            self.received_transactions.add(tx)

    def generate_blocks(self):
        """Generate blocks at exponential intervals using received transactions."""
        while True:
            yield self.env.timeout(np.random.exponential(1 / self.block_rate))  # Wait for next block
            
            if self.received_transactions:  # Only create a block if there are transactions
                block = list(self.received_transactions)  # Copy transactions for block
                self.received_transactions.clear()  # Clear the mempool
   

# Simulation Setup
def simulate(num_nodes=5, tx_rate=0.5, sim_time=10):
    env = simpy.Environment()
    
    # Create nodes with transaction generation process
    nodes = [Node(env, node_id=i, tx_rate=tx_rate) for i in range(num_nodes)]
    
    env.run(until=sim_time)

# Run the simulation
simulate(num_nodes=3, tx_rate=1/2, sim_time=20)