'''
MessagePasser

Created on Mar 12, 2014

@author: Qian Mao
'''

import collections
import logging
import threading

import TCPComm
import yaml


logging.basicConfig()
LOGGER = logging.getLogger("MessagePasser")
LOGGER.setLevel(logging.DEBUG)

# deque for buffering received messages ready to deliver
DELIVERQUE = collections.deque()

# configuration map
CONFMAP = {}
CONF = {}
CONFFILE = None
LOCALNAME = None
localIP = None
localPort = 0

# multicast
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

class Configuration:
    def __init__(self, hosts, groups):
        self.hosts = hosts
        self.groups = groups
    def __repr__(self):
        return "Configuration: \n\thosts: %s\n\tgroups: %s" % (self.hosts, self.groups)
    def getHosts(self):
        return self.hosts
    def getGroups(self):
        return self.groups

# helpful function for message hash key generation
def make_hash(message):
    return hash(message["src"] + str(message["seq"]))

# called by MessagePasser, if the received message is multicast message
def recvMulticastMsg(message):
    # check if the message is new
    msgKey = make_hash(message)
    if msgKey in msgStateMap:
        # update message state
        msgState = msgStateMap[msgKey]
        msgState.memStateMap[message["src"]] = 1
    else:
        msgStateMap[msgKey] = MessageState(message)
        # flood the same message to others, use simple send is enough
        for member in message["memberList"]:
            #if not member == LOCALNAME:
            send(member, message)
        DELIVERQUE.append(message["data"])

# called by application to do a multicast 
def multicast(group, data):
    global LOCALNAME, MULTICAST_SEQ
    memberList = CONF['groups'][group]['members']
    message = {"type" : "MULTICAST",
               "src" : LOCALNAME,
               "seq" : MULTICAST_SEQ,
               "group" : group,
               "memberList" : memberList,
               "data" : data
               }
    MULTICAST_SEQ = MULTICAST_SEQ + 1
    for member in memberList:
        #if not member == LOCALNAME:
        send(member, message)

# a background thread keep receiving message from TCPComm
def receiveThread():
    global DELIVERQUE
    while True:
        message = TCPComm.receive()
        if message != None:
            # check the type of the message
            type = message["type"]
            if type == "NORMAL":
                DELIVERQUE.append(message["data"])
            elif type == "MULTICAST":
                recvMulticastMsg(message)
            else:
                DELIVERQUE.append(message["data"])
                
# called by application to send a message
def normalSend(dst, data):
    message = {"type" : "NORMAL",
               "src" : LOCALNAME,
               "seq" : None,
               "group" : None,
               "memberList" : [],
               "data" : data
               }
    send(dst, message)

# call TCPComm.send to send a message
def send(dst, message):
    # check if the dst is in conf list
    if not dst in CONF["hosts"]:
        pass
    
    TCPComm.send(CONF["hosts"][dst]["ip"], CONF["hosts"][dst]["port"], message)

def directSend(dstIP, dstPort, message):
    TCPComm.send(dstIP, dstPort, message)

# called by application to deliver a message
def receive():
    global DELIVERQUE
    if len(DELIVERQUE) > 0:
        return DELIVERQUE.popleft()
    else:
        return None


# initialize configuration and start listning server
def initialize(confFileName, localName):
    global CONF, LOCALNAME
    
    loadConfiguration(confFileName)
    
    # check if localName exists
    global localIP, localPort
    
    if localName in CONF["hosts"]:
        LOCALNAME = localName
        localIP = CONF["hosts"][localName]["ip"]
        localPort = CONF["hosts"][localName]["port"]
        
    if LOCALNAME != None:
        TCPComm.runServer(localIP, localPort, LOCALNAME)
    else:
        # TODO throw an ERROR
        print "NO matched local name"
        pass
    
    # initialize receiving thread
    thread = threading.Thread(target=receiveThread, args = ())
    thread.daemon = True
    thread.start()
    
# check if the configuration file has been modified
def checkConfChange(confFileName):
    #TODO
    pass

# load configuration file
def loadConfiguration(confFileName):
    LOGGER.info("load configuration")
    global CONFFILE, CONF
    confFile = open(confFileName, "r")
    CONFFILE = yaml.load(confFile)
    confFile.close()
    
    # do some pre-processing
    CONF = {'hosts' : {}, "groups" : {}}
    for host in CONFFILE.hosts:
        CONF['hosts'][host['name']] = {'ip' : host['ip'], 'port' : host['port']}
    
    for group in CONFFILE.groups:
        CONF['groups'][group['name']] = {'members' : group['members']}
        
if __name__ == "__main__":
    initialize("../testFile.txt", "alice")
    multicast("group1", "multicast-group1")
    #send('alice', 'normal message')
    while True:
        msg = receive()
        if not msg == None:
            print msg
        pass
