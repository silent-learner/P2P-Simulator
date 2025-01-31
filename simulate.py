import random
from Peer import *
from utils import *
from Transaction import *
from Graph_utils import *
import simpy as sp


n_peers = 15
z0 = 0.2
z1 = 0.3
Ttx = 1
IaT = 15

P2P_network , peers = P2P_network_generate(n_peers, z0, z1)

env = sp.Environment()

transactions = []

def generate_transaction(env, sender : Peer, receiver : Peer): 
    txn = Transaction(env.now,sender,receiver,random.randint(1,15))
    # print(txn)
    # if sender.balance <= txn.amount:
    sender.mempool.append(txn)
    txn.peers_already_received.add(sender.ID)
    # print(f"Txn {txn.TxnID} created by {sender.ID} and added in its mempool at {env.now}.")
    for neigh in sender.neighbours:
        if neigh not in txn.peers_already_received:
            env.process(forward_transaction(env,txn,sender,neigh))


def forward_transaction(env,txn : Transaction,peer1 : Peer,peer2 : Peer):
    latency =  delay(peer1,peer2,1)
    yield env.timeout(latency)

    if txn.TxnID in [trxn.TxnID for trxn in peer2.mempool]:
        return
    peer2.mempool.append(txn)
    # print(f"Txn {txn.TxnID} reached peer {peer2.ID} and added to its mempool at time {env.now}.")
    txn.peers_already_received.add(peer2.ID)
    for neigh in peer2.neighbours:
        if neigh != peer1 and neigh not in txn.peers_already_received:
            env.process(forward_transaction(env,txn,peer2,neigh))


def process_transaction(env):
    pass


def forward_block(env,block : Block,peer : Peer, peer2 : Peer):
    latency =  delay(peer,peer2,len(block.TxnList))
    yield env.timeout(latency)

    print(f'Peer {peer2.ID} nodes {[blk.BlkId for blk in peer2.ledger.nodes]}')
    if peer2.ID in block.peers_already_received:
        print(f"returning from Peer {peer2.ID} since block {block.BlkId} is already here.!!")
        return 
     #//TODO: validate


    lengths = nx.single_source_shortest_path_length(peer2.ledger,source=peer2.genesis)
    longest_chain_node = None
    max_length = -1
    for blk in lengths:
        if lengths[blk] > max_length:
            longest_chain_node = blk
            max_length = lengths[blk]
    
    print(f"Block {block.BlkId} reached peer {peer2.ID} and added to its ledger at time {env.now}.")
    print(f"Peer {peer2.ID} previuos ledger",[blk.BlkId for blk in peer2.ledger.nodes])

    block.peers_already_received.add(peer2.ID)
    print(f'Longest node {longest_chain_node.BlkId} for {peer2.ID} at {env.now}')
    peer2.ledger.add_node(block)
    peer2.Tree.add(block.BlkId)
    peer2.ledger.add_edge(longest_chain_node,block)

    print(f"Peer {peer2.ID} updated ledger",[blk.BlkId for blk in peer2.ledger.nodes])

    for neigh in peer2.neighbours:
        if neigh != peer and neigh.ID not in block.peers_already_received:
            print(f"Forwarding from forward fucntion-- Block {block.BlkId} to Peer {neigh.ID} from Peer {peer2.ID}")
            env.process(forward_block(env,block,peer2,neigh))



def generate_block(env,peer :Peer):
    txns = peer.mempool
    lengths = nx.single_source_shortest_path_length(peer.ledger,source=peer.genesis)
    longest_chain_node = None
    max_length = -1
    for blk in lengths:
        if lengths[blk] > max_length:
            longest_chain_node = blk
            max_length = lengths[blk]

    print(f"Peer {peer.ID} starts mining at {env.now}.")
    mining_time = random.expovariate(peer.hashingPower/IaT) #//TODO:
    #//TODO:
    yield env.timeout(mining_time)
    print(f"Peer {peer.ID} ends mining at {env.now}.")

    lengths = nx.single_source_shortest_path_length(peer.ledger,source=peer.genesis)
    longest_chain_node_new = None
    max_length = -1
    for blk in lengths:
        if lengths[blk] > max_length:
            longest_chain_node_new = blk
            max_length = lengths[blk]

    if longest_chain_node != longest_chain_node_new:
            print(f"Peer {peer.ID} was slow in mining someone else mined first.")

    print(f'Longest node {longest_chain_node.BlkId} for {peer.ID} at {env.now} before mining')
    print(f'Longest node {longest_chain_node_new.BlkId} for {peer.ID} at {env.now} after mining')
    # if longest_chain_node == longest_chain_node_new:
    block = Block(peer,env.now,longest_chain_node,txns)
                # peer.mempool.clear()
    block.TxnList.append(Transaction(env.now,peer,None,50)) # coinbase
    block.peers_already_received.add(peer.ID)
    print(f"Block {block.BlkId} mined by {peer.ID} and added in its ledger at {env.now}.")
    print(f"Peer {peer.ID} previous ledger",[blk.BlkId for blk in peer.ledger.nodes])
    peer.Tree.add(block.BlkId)
    peer.ledger.add_node(block)
    peer.ledger.add_edge(longest_chain_node,block)
    print(f"Peer {peer.ID} updated ledger",[blk.BlkId for blk in peer.ledger.nodes])

    for neigh in peer.neighbours:
            if neigh.ID not in block.peers_already_received:
                print(f"Forwarding from generator function -- Block {block.BlkId} to Peer {neigh.ID} from Peer {peer.ID}")
                env.process(forward_block(env,block,peer,neigh))
    # else:
    #     print(f"Peer {peer.ID} was slow in mining someone else mined first.")

for peer in peers:
    # 1. generate first transaction for each peer
    filtered_peer = [x for x in peers if x != peer]
    def transaction_generator_for_every_peer(env, peer, filtered_peer):
        while True:
            waitTime = random.expovariate(1 / Ttx)
            yield env.timeout(waitTime)
            generate_transaction(env, peer, random.choice(filtered_peer))

    env.process(transaction_generator_for_every_peer(env, peer, filtered_peer))
    # 2. whenever a transaction is processed, another transaction is generated

for peer in peers:

    def block_generator_for_every_peer(env,peer : Peer):
        while True:
            interarrival_blovk_time = random.expovariate(1/IaT)
            yield env.timeout(interarrival_blovk_time)
            yield env.process(generate_block(env, peer))

    env.process(block_generator_for_every_peer(env,peer))


# for peer in peers:
#     print(peer.ID)
#     for key , value in peer.prop_delays.items():
#         print('\t',key,value)

env.run(until=300)



for peer in peers:
    print(peer.ID,peer.isSlow,peer.hashingPower)
    for txn in peer.mempool:
        print('\t',txn)
    # nx.draw(peer.ledger,labels={n: n.BlkId for n in peer.ledger.nodes})
    # plt.savefig(f'Blockchain{peer.ID}.png')
    # plt.clf()
    make_blockChainTree(peer.ledger,peer.genesis,f'./BlockChainTrees/Tree {peer.ID}.png')
    print()


print("------------------------------------The end--------------------------------------------")
