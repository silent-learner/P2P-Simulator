from Peer import *
import random

def delay(A : Peer , B : Peer):
        prop_delay = A.prop_delays[B.ID]
        cij = 5000000 if A.isSlow or B.isSlow else 100000000
        trn_delay = (1024*8)/cij
        queing_delay = random.expovariate(cij/96000)
        return prop_delay + queing_delay + trn_delay