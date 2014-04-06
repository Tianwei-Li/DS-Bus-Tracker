'''
Created on Apr 5, 2014

@author: maoqian
'''

class GSNAction(object):
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

turnOn = GSNAction("turnOn")
recvUserReq = GSNAction("recvUserReq")
recvBusReq = GSNAction("recvBusReq")
timeout = GSNAction("timeout")
turnOff = GSNAction("turnOff")

