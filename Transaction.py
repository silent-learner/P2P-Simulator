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

    def __str__(self):
        return f'{self.message}'
