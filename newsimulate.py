import random
from Peer import *
from utils import *
from Transaction import *
from Graph_utils import *
import simpy as sp

n_peers = 7
z0 = 0.2
z1 = 0.3
Ttx = 5
IaT = 10

P2P_network, peers = P2P_network_generate(n_peers, z0, z1)

env = sp.Environment()


def generate_transaction(env, sender: Peer, receiver: Peer):
    txn = Transaction(env.now, sender, receiver, random.randint(1, 5))
    sender.mempool.append(txn)
    print(
        f"{env.now}: P{sender.ID}: Txn {txn.TxnID} created by {sender.ID}: P{txn.sender.ID} to P{txn.receiver.ID} coins={txn.amount}"
    )
    for neigh in sender.neighbours:
        env.process(forward_transaction(env, txn, sender, neigh))


def forward_transaction(env, txn: Transaction, peer1: Peer, peer2: Peer):
    latency = delay(peer1, peer2, 1)
    yield env.timeout(latency)
    if txn.TxnID in [trxn.TxnID for trxn in peer2.mempool]:
        return
    peer2.mempool.append(txn)
    print(f"{env.now}: P{peer2.ID}: Txn {txn.TxnID} received by {peer2.ID}.")
    for neigh in peer2.neighbours:
        if neigh != peer1:
            env.process(forward_transaction(env, txn, peer2, neigh))


def generate_block(env, peer: Peer):
    lengths = nx.single_source_shortest_path_length(peer.ledger, source=peer.genesis)
    paths = nx.single_source_shortest_path(peer.ledger, source=peer.genesis)
    longest_chain_node = max(lengths, key=lengths.get)

    transactions_in_the_longest_path = []
    for blk in paths[longest_chain_node]:
        transactions_in_the_longest_path.extend(blk.TxnList)

    transactions_to_be_inserted_in_new_block = []
    number_of_transactions_the_new_block_can_accomodate = 998
    # 998 because max size is 1000 KB
    # 1 KB metadata
    # 1 KB for coinbase Txn
    for txn in peer.mempool:
        if number_of_transactions_the_new_block_can_accomodate <= 0:
            break
        if txn not in transactions_in_the_longest_path:
            transactions_to_be_inserted_in_new_block.append(txn)
            number_of_transactions_the_new_block_can_accomodate -= 1

    mining_time = random.expovariate(peer.hashingPower / IaT)
    yield env.timeout(mining_time)

    lengths = nx.single_source_shortest_path_length(peer.ledger, source=peer.genesis)
    longest_chain_node_new = max(lengths, key=lengths.get)

    if longest_chain_node != longest_chain_node_new:
        return

    block = Block(
        peer, env.now, longest_chain_node, transactions_to_be_inserted_in_new_block
    )
    block.TxnList.append(
        Transaction(env.now, None, peer, 50)
    )  # add coinbase txn to block
    print(
        f"{env.now}: P{peer.ID}: Block {block.BlkId} mined by {peer.ID} and added in its ledger"
    )
    peer.Tree.add(block)
    peer.ledger.add_node(block)
    peer.ledger.add_edge(longest_chain_node, block)
    print(
        f"{env.now}: P{peer.ID}: Peer {peer.ID} updated ledger",
        [blk.BlkId for blk in peer.ledger.nodes],
    )

    # if longest_chain_node == longest_chain_node_new:
    # peer.everyones_balance[peer.ID] += 50
    for neigh in peer.neighbours:
        print(
            f"{env.now}: P{peer.ID}: Forwarding from generator function -- Block {block.BlkId} to Peer {neigh.ID} from Peer {peer.ID}"
        )
        env.process(forward_block(env, block, peer, neigh))
    # else:
    #     print(f"Peer {peer.ID} was slow in mining someone else mined first.")
