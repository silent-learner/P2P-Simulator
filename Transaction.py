import Peer
import random
from utils import *


class Transaction:
    uID = 0  # a static variable to make sure that TxnIDs are unique

    # static array to keep track of the transactions
    # transaction[txnID] should give you the entire Transaction
    transactions = []

    def __init__(self, time, sender: Peer, receiver: Peer, amount):
        self.TxnID = Transaction.uID
        Transaction.uID += 1
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.time = time
        self.message = (
            f"Txn-{self.TxnID}: P{sender.ID} pays P{receiver.ID} {amount} coins."
            if sender is not None
            else f"Txn-{self.TxnID}: P{receiver.ID} mines 50 coins."
        )
        Transaction.transactions.append(self)

    def __str__(self):
        return f"{self.time}: {self.message}"


def forward_transaction(
    env,
    txnID,
    peer1: Peer,
    peer2: Peer,
    P2P_network: nx.Graph,
):
    # calculate latency and wait for that much time
    latency = delay(peer1, peer2, 1, P2P_network)
    yield env.timeout(latency)
    
    if txnID in peer2.mempool:
        return
    peer2.mempool.append(txnID)
    print(f"{env.now}: Txn-{txnID}: received by P{peer2.ID}.")
    for neighID in P2P_network[peer2.ID]:
        if neighID != peer2.ID:
            env.process(
                forward_transaction(env, txnID, peer2, Peer.peers[neighID], P2P_network)
            )


def generate_transaction(env, sender: Peer, receiver: Peer, P2P_network: nx.Graph):
    transaction_amount = random.randint(1, 5)
    
    # dont generate transaction if the amount of transaction
    # is greater than the sender's balance
    if transaction_amount > sender.everyones_balance[sender.ID]:
        return
    txn = Transaction(env.now, sender, receiver, transaction_amount)
    sender.mempool.append(txn.TxnID)
    print(txn)

    # iterate over the neighbours and
    # broadcast the transaction to the neighbours
    for neighID in P2P_network[sender.ID]:
        env.process(
            forward_transaction(
                env,
                txnID=txn.TxnID,
                peer1=sender,
                peer2=Peer.peers[neighID],
                P2P_network=P2P_network,
            )
        )
