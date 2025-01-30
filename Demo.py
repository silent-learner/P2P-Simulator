import simpy
import numpy as np

class Node:
    def __init__(self, env, node_id, tx_rate):
        """
        Initialize a node in the network.
        
        :param env: SimPy environment
        :param node_id: Unique ID of the node
        :param tx_rate: Rate parameter (1/Tx) for exponential distribution
        """
        self.env = env
        self.node_id = node_id
        self.tx_rate = tx_rate
        self.tx_count = 0  # Track number of transactions generated
        self.process = env.process(self.generate_transactions())  # Start transaction generation

    def generate_transactions(self):
        """Process for generating transactions at random exponential intervals."""
        while True:
            interarrival_time = np.random.exponential(1 / self.tx_rate)  # Exponential delay
            yield self.env.timeout(interarrival_time)  # Wait for the next transaction
            self.tx_count += 1
            print(f'Time {self.env.now:.2f}: Node {self.node_id} generated Transaction {self.tx_count}')

# Simulation Setup
def simulate(num_nodes=5, tx_rate=0.5, sim_time=10):
    env = simpy.Environment()
    
    # Create nodes with transaction generation process
    nodes = [Node(env, node_id=i, tx_rate=tx_rate) for i in range(num_nodes)]
    
    env.run(until=sim_time)

# Run the simulation
simulate(num_nodes=3, tx_rate=1/2, sim_time=20)