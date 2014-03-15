'''
MessagePasser

Created on Mar 12, 2014

@author: Qian Mao
'''

import collections
import logging

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



# called by application to send a message
def send(dst, message):
    # check if the dst is in conf list
    if not dst in CONF["hosts"]:
        pass
    
    TCPComm.send(CONF["hosts"][dst]["ip"], CONF["hosts"][dst]["port"], message)

# called by application to deliver a message
def receive():
    return TCPComm.receive()

# called by application to multicast
def multicast(groupName, message):
    pass

# initialize configuration and start listning server
def initialize(confFileName, localName):
    global CONF, LOCALNAME
    
    loadConfiguration(confFileName)
    
    # check if localName exists
    localIP,localPort = None, 0
    
    if localName in CONF["hosts"]:
        LOCALNAME = localName
        localIP = CONF["hosts"][localName]["ip"]
        localPort = CONF["hosts"][localName]["port"]
        
    if LOCALNAME != None:
        TCPComm.runServer(localIP, localPort)
    else:
        # TODO throw an ERROR
        print "NO matched local name"
        pass
    
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

if __name__ == "__main__":
    initialize("../testFile.txt", "alice")
    while True:
        pass
