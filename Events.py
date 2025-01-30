import simpy
import random

def generate_transactions():
        """Process for generating transactions at random exponential intervals."""
        while True:
            interarrival_time = random.exponential(1 / self.tx_rate)  # Exponential delay
            yield self.env.timeout(interarrival_time)  # Wait for the next transaction
            self.tx_count += 1
            print(f'Time {self.env.now:.2f}: Node {self.node_id} generated Transaction {self.tx_count}')