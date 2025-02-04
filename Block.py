from Peer import *
from Transaction import *
from utils import *


class Block:
    # static array to keep track of the blocks
    # blocks[BlkId] should give you the entire block
    blocks = []
    count = 0
    TxnList: list[Transaction] = []

    def __init__(self, TxnList=[], parentID=-1):
        self.BlkId = Block.count
        Block.count += 1
        self.TxnList = TxnList.copy()
        self.parentID = parentID
        Block.blocks.append(self)


def is_valid_transactions_array(txnID_list):
    initial_balance = Peer.initial_balances.copy()
    for txnID in txnID_list:
        txn = Transaction.transactions[txnID]
        if txn.sender:
            initial_balance[txn.sender.ID] -= txn.amount
        initial_balance[txn.receiver.ID] += txn.amount
    return min(initial_balance) >= 0


def forward_block(env, block: Block, peer: Peer, peer2: Peer, P2P_network: nx.Graph):
    # calculate latency and wait for that much time
    latency = delay(peer, peer2, len(block.TxnList), P2P_network)
    yield env.timeout(latency)

    if block.BlkId in peer2.blockList:
        return
    peer2.blockList.append(block.BlkId)
    print(f"{env.now}: Block-{block.BlkId}: received by P{peer2.ID}.")

    # check if parent Node exist in the ledger
    if block.parentID not in peer2.ledger:
        print(f"{env.now}: Block-{block.BlkId}: rejected by P{peer2.ID}.")
        return

    # find the path from genesis node to the parent
    peer2.ledger.add_node(block.BlkId)
    path = nx.shortest_path(peer2.ledger, 0, block.parentID)

    # validate the block
    transactions_in_this_chain = []
    for blkID in path:
        transactions_in_this_chain.extend(Block.blocks[blkID].TxnList)
    transactions_in_this_chain.extend(block.TxnList)

    if not is_valid_transactions_array(transactions_in_this_chain):
        print(f"{env.now}: Block-{block.BlkId}: rejected by P{peer2.ID}.")
        return
    print(f"{env.now}: Block-{block.BlkId}: validated by P{peer2.ID}.")

    # add it to its ledger
    peer2.ledger.add_node(block.BlkId)
    peer2.ledger.add_edge(block.parentID, block.BlkId)
    print(f"{env.now}: P{peer2.ID}: New block in its tree: Block-{block.BlkId}.")

    # forward to other peers
    for neighID in P2P_network[peer2.ID]:
        if neighID != peer2.ID:
            env.process(
                forward_block(env, block, peer2, Peer.peers[neighID], P2P_network)
            )


def generate_block(env, peer: Peer, IaT, P2P_network: nx.Graph):
    # zero is the id of genesis block

    # find the length of the longest path in
    # the blockchain tree of the current peer
    lengths = nx.single_source_shortest_path_length(peer.ledger, source=0)
    paths = nx.single_source_shortest_path(peer.ledger, source=0)
    longest_chain_node = max(lengths, key=lengths.get)

    # store all the transactions found
    # in the logest chain in a list
    transactions_in_the_longest_path = []
    for blk in paths[longest_chain_node]:
        transactions_in_the_longest_path.extend(Block.blocks[blk].TxnList)

    transactions_to_be_inserted_in_new_block = []
    number_of_transactions_the_new_block_can_accomodate = 998
    # 998 because max size is 1000 KB
    # 1 KB metadata
    # 1 KB for coinbase Txn

    # only add those transactions to the block that are
    # not present in the longest chain before mining
    for txnID in peer.mempool:
        if number_of_transactions_the_new_block_can_accomodate <= 0:
            break
        if txnID not in transactions_in_the_longest_path:
            transactions_to_be_inserted_in_new_block.append(txnID)
            number_of_transactions_the_new_block_can_accomodate -= 1

    # if the set of these transactions are valid
    # only then start mining
    # else return
    # validate these set of transactions
    if not is_valid_transactions_array(
        [*transactions_in_the_longest_path, *transactions_to_be_inserted_in_new_block]
    ):
        return

    print(f"{env.now}: P{peer.ID}: starts mining B{longest_chain_node}")

    # mine the blocks for some time
    mining_time = random.expovariate(peer.hashingPower / IaT)
    yield env.timeout(mining_time)

    # calculate the longest chain again
    # if the longest chain is the same then we have successfully mined the block
    # else peer was slow and someone else mined that block
    lengths = nx.single_source_shortest_path_length(peer.ledger, source=0)
    longest_chain_node_new = max(lengths, key=lengths.get)

    print(f"{env.now}: P{peer.ID}: ends mining B{longest_chain_node}")
    if longest_chain_node != longest_chain_node_new:
        print(f"{env.now}: P{peer.ID}: was slow in mining.")
        return

    # mining successful
    # create a new block and add it to the longest chain
    # create a coinbase transaction and include it in this block
    coinbase_txn = Transaction(time=env.now, sender=None, receiver=peer, amount=50)
    transactions_to_be_inserted_in_new_block.append(coinbase_txn.TxnID)
    block = Block(
        TxnList=transactions_to_be_inserted_in_new_block, parentID=longest_chain_node
    )
    print(coinbase_txn)

    # add the block in the tree of peer
    peer.ledger.add_node(block.BlkId)
    peer.ledger.add_edge(longest_chain_node, block.BlkId)
    print(f"{env.now}: P{peer.ID}: mined Block-{block.BlkId}.")
    print(f"{env.now}: P{peer.ID}: New block in its tree: Block-{block.BlkId}.")
    peer.everyones_balance[peer.ID] += 50

    # broadcast this coinbase transaction to the neighbours
    peer.mempool.append(coinbase_txn.TxnID)
    for neighID in P2P_network[peer.ID]:
        env.process(
            forward_transaction(
                env,
                txnID=coinbase_txn.TxnID,
                peer1=peer,
                peer2=Peer.peers[neighID],
                P2P_network=P2P_network,
            )
        )

    # broadcast our new block to the neighbours
    peer.blockList.append(block.BlkId)
    for neighID in P2P_network[peer.ID]:
        env.process(
            forward_block(
                env,
                block=block,
                peer=peer,
                peer2=Peer.peers[neighID],
                P2P_network=P2P_network,
            )
        )
