'''
Network level utility

Created on Mar 12, 2014

@author: Qian Mao
'''

import TCPComm
import collections
import yaml
import logging

logging.basicConfig()
LOGGER = logging.getLogger("MessagePasser")
LOGGER.setLevel(logging.DEBUG)

# deque for buffering received messages ready to deliver
DELIVERQUE = collections.deque()

# configuration map
CONFMAP = {}
CONF = None
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
    pass

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
    
    for host in getattr(CONF, "hosts"):
        if localName == host["name"]:
            LOCALNAME = localName
            localIP = host["ip"]
            localPort = host["port"]
            break
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
    global CONF
    confFile = open(confFileName, "r")
    CONF = yaml.load(confFile)
    confFile.close()

if __name__ == "__main__":
    initialize("../testFile", "alice")
    while True:
        pass
