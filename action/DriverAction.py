'''
Created on Apr 5, 2014

@author: Terry Li
'''

class DriverAction(object):
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

turnOn = DriverAction("turnOn")
start = DriverAction("start")
recvGSNAck = DriverAction("recvGSNAck")
recvRSNAck = DriverAction("recvRSNAck")
recvLocReq = DriverAction("recvLocReq")
turnOff = DriverAction("turnOff")

timeout = DriverAction("timeout")

