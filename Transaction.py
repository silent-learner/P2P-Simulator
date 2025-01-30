import random
import uuid
import Peer

class Transaction:
    def __init__(self,time,sender : Peer,receiver : Peer, amount):
        self.TxnID = uuid.uuid4()
        self.time = time
        self.message = f'{self.TxnID}: {sender.ID} pays {receiver.ID} {amount} coins.'
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def delay(self, A : Peer , B : Peer):
        prop_delay = random.uniform(10/1000,500/1000)
        cij = 5000000 if A.isSlow or B.isSlow else 100000000
        trn_delay = (1024*8)/cij
        queing_delay = random.expovariate(cij/96000)
        return prop_delay + queing_delay + trn_delay

    def __str__(self):
        return f'{self.message}'
