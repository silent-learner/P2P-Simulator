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

P2P_network , peers = P2P_network_generate(n_peers, z0, z1)

env = sp.Environment()

transactions = []

def generate_transaction(env, sender : Peer, receiver : Peer): 
    txn = Transaction(env.now,sender,receiver,random.randint(1,5))
    # print(txn)
    # if sender.balance <= txn.amount:
    sender.mempool.append(txn)
    # txn.peers_already_received.add(sender.ID)
    # print(f"Txn {txn.TxnID} created by {sender.ID} sender balance {sender.balance} amount {txn.amount} and added in its mempool at {env.now}.")
    print(f"{env.now}: Txn {txn.TxnID} created by {sender.ID}.")
    for neigh in sender.neighbours:
        # if neigh not in txn.peers_already_received:
        env.process(forward_transaction(env,txn,sender,neigh))


def forward_transaction(env,txn : Transaction,peer1 : Peer,peer2 : Peer):
    latency =  delay(peer1,peer2,1)
    yield env.timeout(latency)

    if txn.TxnID in [trxn.TxnID for trxn in peer2.mempool]:
        return
    peer2.mempool.append(txn)
    print(f"{env.now}: Txn {txn.TxnID} received by {peer2.ID}.")
    # print(f"Txn {txn.TxnID} reached peer {peer2.ID} and added to its mempool at time {env.now}.")
    # txn.peers_already_received.add(peer2.ID)
    for neigh in peer2.neighbours:
        if neigh != peer1:
            env.process(forward_transaction(env,txn,peer2,neigh))


def forward_block(env,block : Block,peer : Peer, peer2 : Peer):
    latency =  delay(peer,peer2,len(block.TxnList))
    yield env.timeout(latency)

    if block.BlkId in peer2.blocklist:
        print(f"{env.now}: Returning from Peer {peer2.ID} since block {block.BlkId} is already here.!!")
        return 
    
    peer2.blocklist.append(block.BlkId)
    print(f"{env.now}: Peer {peer2.ID} received block {block.BlkId}.")

    #  validate
    for txn in block.TxnList:
        if txn.sender is not None and txn.sender.balance < txn.amount:
            print(f"{env.now}: Block {block.BlkId} is discarded by peer {peer2.ID} since Txn {txn.TxnID} is invalid.")
            return

    # all txns are valid now update balance of sender and receiver
    for txn in block.TxnList:
        print(f'{env.now}:  here for txn {txn.TxnID}')
        if txn.sender is not None: # not coinbase txn 
            txn.sender.balance -= txn.amount
            txn.receiver.balance += txn.amount

    lengths = nx.single_source_shortest_path_length(peer2.ledger,source=peer2.genesis)
    longest_chain_node = None
    max_length = -1
    for blk in lengths:
        if lengths[blk] > max_length:
            longest_chain_node = blk
            max_length = lengths[blk]
    
    print(f"{env.now}: Block {block.BlkId} reached peer {peer2.ID} and added to its ledger.")
    print(f"{env.now}: Peer {peer2.ID} previuos ledger",[blk.BlkId for blk in peer2.ledger.nodes])

    print(f'{env.now}: Longest node {longest_chain_node.BlkId} for {peer2.ID}')
    peer2.ledger.add_node(block)
    peer2.Tree.add(block)
    peer2.ledger.add_edge(longest_chain_node,block)

    print(f"{env.now}: Peer {peer2.ID} updated ledger",[blk.BlkId for blk in peer2.ledger.nodes])


    for neigh in peer2.neighbours:
        if neigh != peer:
            print(f"{env.now}: Forwarding from forward fucntion-- Block {block.BlkId} to Peer {neigh.ID} from Peer {peer2.ID}")
            env.process(forward_block(env,block,peer2,neigh))



def generate_block(env,peer :Peer):
    lengths = nx.single_source_shortest_path_length(peer.ledger,source=peer.genesis)
    paths = nx.single_source_shortest_path(peer.ledger, source=peer.genesis)
    longest_chain_node = max(lengths, key=lengths.get)
    longest_path = paths[longest_chain_node]
    print(f'{env.now}: Length of the longest path: {len(paths[longest_chain_node])}')
    print(f'{env.now}: path: {[e.BlkId for e in longest_path]}')
    print(f"{env.now}: Peer {peer.ID} starts mining")

    transactions_in_the_longest_path = []
    for blk in paths[longest_chain_node]:
        transactions_in_the_longest_path.extend(blk.TxnList)

    print(f"{env.now}: Transactions in the longest chain: {len(transactions_in_the_longest_path)}")

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
        
    print(f"{env.now}: Transactions to be inserted in new block: {len(transactions_to_be_inserted_in_new_block)}")

    mining_time = random.expovariate(peer.hashingPower/IaT) #//TODO:
    print(f'{env.now}: Longest node {longest_chain_node.BlkId} for {peer.ID} before mining')
    yield env.timeout(mining_time)


    lengths = nx.single_source_shortest_path_length(peer.ledger,source=peer.genesis)
    longest_chain_node_new = max(lengths, key=lengths.get)

    print(f"{env.now}: Peer {peer.ID} ends mining")
    print(f'{env.now}: Longest node {longest_chain_node_new.BlkId} for {peer.ID} after mining')

    if longest_chain_node != longest_chain_node_new:
        print(f"{env.now}: Peer {peer.ID} was slow in mining someone else mined first.")
        return

    # if longest_chain_node == longest_chain_node_new:
    block = Block(peer,env.now,longest_chain_node,transactions_to_be_inserted_in_new_block)
    block.TxnList.append(Transaction(env.now,None,peer,50)) # add coinbase txn to block
    print(f"{env.now}: Block {block.BlkId} mined by {peer.ID} and added in its ledger")
    print(f"{env.now}: Peer {peer.ID} previous ledger",[blk.BlkId for blk in peer.ledger.nodes])
    peer.Tree.add(block)
    peer.ledger.add_node(block)
    peer.ledger.add_edge(longest_chain_node,block)
    print(f"{env.now}: Peer {peer.ID} updated ledger",[blk.BlkId for blk in peer.ledger.nodes])

    # if longest_chain_node == longest_chain_node_new:
    peer.balance += 50
    for neigh in peer.neighbours:
        print(f"{env.now}: Forwarding from generator function -- Block {block.BlkId} to Peer {neigh.ID} from Peer {peer.ID}")
        env.process(forward_block(env,block,peer,neigh))
    # else:
    #     print(f"Peer {peer.ID} was slow in mining someone else mined first.")

for peer in peers:
    # possible_receivers is the array of peers except the current peer
    possible_receivers = [x for x in peers if x != peer]
    def transaction_generator_for_every_peer(env, peer, possible_receivers):
        while True:
            waitTime = random.expovariate(1 / Ttx)
            yield env.timeout(waitTime)
            generate_transaction(env, peer, random.choice(possible_receivers))

    env.process(transaction_generator_for_every_peer(env, peer, possible_receivers))

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

env.run(until=100)



for peer in peers:
    print(peer.ID,peer.isSlow,peer.hashingPower,peer.balance)
    # for txn in peer.mempool:
    #     print('\t',txn)
    # for block in peer.ledger.nodes():
    #     for txn in block.TxnList:
    #         print(txn)
    # nx.draw(peer.ledger,labels={n: n.BlkId for n in peer.ledger.nodes})
    # plt.savefig(f'Blockchain{peer.ID}.png')
    make_blockChainTree(peer.ledger,peer.genesis,f'./BlockChainTrees/Block Chain Tree {peer.ID}.png')
    plt.clf()
    print()

for peer in peers:
        print(f"Peer {peer.ID} blockchain tree")
        for block in peer.Tree:
            print('\t',block)

print("------------------------------------The end--------------------------------------------")
