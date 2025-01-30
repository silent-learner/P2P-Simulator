import Peer

class Transaction:
    uID = 0
    def __init__(self,time,sender : Peer,receiver : Peer, amount):
        self.TxnID = Transaction.uID
        self.time = time
        self.message = f'{self.TxnID}: {sender.ID} pays {receiver.ID} {amount} coins.'
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.peers_already_received = set()
        Transaction.uID += 1

    def __str__(self):
        return f'{self.time} -- {self.message}'
