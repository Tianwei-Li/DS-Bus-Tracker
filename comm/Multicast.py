'''
Created on Mar 15, 2014

@author: Qian Mao
'''

import TCPComm

MULTICAST_SEQ = 0

holdBackQueue = []
# key is message src+seq
msgStateMap = {}

class MessageState:
    def __init__(self, message):
        self.message = message
        self.group = message["group"]
        self.memberList = message["memberList"]
        self.memStateMap = dict.fromkeys(self.memberList, 0)
        
    def __repr__(self):
        return "MessageState: \n\tgroup: %s\n\tmessage: %s\n\tmemStateMap: %s" % (self.group, self.message, self.memStateMap)

# helpful function for message hash key generation
def make_hash(message):
    return hash(message["src"] + message["seq"])

# called by MessagePasser, if the received message is multicast message
def recvMulticastMsg(message):
    # check if the message is new
    msgKey = make_hash(message)
    if msgKey in msgStateMap:
        # update message state
        msgState = msgStateMap[msgKey]
        msgState.memStateMap[message["src"]] = 1
        print msgState
    else:
        msgStateMap[msgKey] = MessageState(message)
    
def multicast(TCPComm, src, group, memberList, data):
    message = {"type" : "MULTICAST",
               "src" : src,
               "seq" : MULTICAST_SEQ,
               "group" : group,
               "memberList" : memberList,
               "data" : data
               }
    for member in memberList:
        TCPComm

if __name__ == "__main__":
    message = {"type" : "MULTICAST",
               "src" : "bob",
               "seq" : "123",
               "group" : "test_group",
               "memberList" : ["alice", "bob"],
               "data" : "hello, this is a sample"
               }
    recvMulticastMsg(message)
    recvMulticastMsg(message)

