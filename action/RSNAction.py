'''
Created on Apr 5, 2014

@author: Terry Li
'''

class RSNAction(object):
    '''
    classdocs
    '''

    def __init__(self, action):
        self.action = action
        
    def __str__(self): 
        return self.action
    
    def __cmp__(self, other):
        return cmp(self.action, other.action)
    # Necessary when __cmp__ or __eq__ is defined
    # in order to make this class usable as a
    # dictionary key:
    def __hash__(self):
        return hash(self.action)

turnOn = RSNAction("turnOn")
recvGSNAck = RSNAction("recvGSNAck")
askBusLoc = RSNAction("askBusLoc")
recvLocReq = RSNAction("recvLocReq")
recvGSNHB = RSNAction("recvGSNHB")           # receive GSN heart beat
recvBusChange = RSNAction("recvBusChange")   # receive bus add or remove request form GSN
recvRSNAssign = RSNAction("recvRSNAssign")   # receive gsn message to indicate it is the new RSN
recvDriverLoc = RSNAction("recvDriverLoc")
recvRSNResign = RSNAction("recvRSNResign")

timeout = RSNAction("timeout")
turnOff = RSNAction("turnOff")


