'''
Created on Apr 2, 2014

@author: Qian Mao
'''

import comm.MessagePasser as MessagePasser
import time

LOCALNAME = None
ROLE = None
STATE = None


# must be first called by GUI app 
def initialize(conf, localName, role):
    global LOCALNAME, ROLE
    LOCALNAME = localName
    ROLE = role
    
    MessagePasser.initialize(conf, localName)
    
# request by GUI app to find the nearest bus
def request(routeNo, direction, destination):
    pass



if __name__ == '__main__':
    MessagePasser.initialize("../testFile.txt", "alice")
    MessagePasser.normalSend("alice", "hi alice")
    time.sleep(2)
    print MessagePasser.receive()

