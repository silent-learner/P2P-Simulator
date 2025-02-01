import random
import Peer

class Block:
    count = 0
    def __init__(self,miner,time,prevBlock,TxnList=[]):
        print("Block prev ",prevBlock)
        self.BlkId = Block.count
        self.time = time
        self.miner = miner
        self.prevBlock = prevBlock
        self.TxnList = TxnList
        self.peers_already_received = set()
        Block.count += 1


    def delay(self, A : Peer ,B : Peer):
        prop_delay = random.uniform(10/1000,500/1000)
        cij = 5000000 if A.isSlow or B.isSlow else 100000000
        num_txns = len(self.TxnList)+1
        trn_delay = (1024*8*(num_txns))/cij
        queing_delay = random.expovariate(cij/96000)
        return prop_delay + queing_delay + trn_delay

    def __str__(self):
        prevID = self.prevBlock.BlkId if self.prevBlock is not None else "None"
        minerID = self.miner.ID if self.miner is not None else "None"
        return f' Block {self.BlkId} --- prevBlock {prevID} --------- mined by {minerID} at {self.time}.'
