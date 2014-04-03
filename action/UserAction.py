'''
Created on Apr 2, 2014

@author: Qian Mao
'''

class UserAction(object):
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

turnOn = UserAction("turnOn")
initialize = UserAction("initialize")
pingGSN = UserAction("pingGSN")
timeout = UserAction("timeout")
recvAck = UserAction("recvAck")
request = UserAction("request")
recvRes = UserAction("recvRes")
turnOff = UserAction("turnOff")
