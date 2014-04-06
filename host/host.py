'''
Created on Apr 2, 2014

@author: Qian Mao
'''
import sys
sys.path += ['../']

import comm.MessagePasser as MessagePasser
import state.UserStates as UserStates
import state.GSNStates as GSNStates
import time
import collections
import threading
import logging


logging.basicConfig()
LOGGER = logging.getLogger("Host")
LOGGER.setLevel(logging.DEBUG)

LOCALNAME = None
ROLE = None
STATE = None
USERSM = None
DRIVERSM = None

DISPATCHERMAP = {}
DISPATCH_QUEUE = collections.deque()

# a background thread keep dispatching messages from DISPATCH_QUEUE
def dispatcherThread():
    global DISPATCH_QUEUE
    while True:
        if DISPATCH_QUEUE:
            message = DISPATCH_QUEUE.popleft()
            if not message == None:
                dispatch(message)
        time.sleep(0.05)

# a background thread keep receiving messages from MP
def receiveThread():
    global DISPATCH_QUEUE
    while True:
        message = MessagePasser.receive()
        if message != None:
            # TODO: check the type of the message
            DISPATCH_QUEUE.append(message)
        time.sleep(0.05)

# must be first called by GUI app 
def initialize(conf, localName, role):
    global LOCALNAME, ROLE, USERSM
    LOCALNAME = localName
    ROLE = role
    MessagePasser.initialize(conf, localName)
    
    LOGGER.info("Initializing Host")
    
    # initialize dispatching and receiving thread
    recv_thread = threading.Thread(target=receiveThread, args = ())
    recv_thread.daemon = False
    recv_thread.start()
    
    dipatch_thread = threading.Thread(target=dispatcherThread, args = ())
    dipatch_thread.daemon = True
    dipatch_thread.start()
    
    # start state machine
    if ROLE == "USER":
        UserStates.initialize()
        DISPATCHERMAP["USER_SM"] = UserStates
        
        # turnOn the machine
        enqueue({"SM":"USER_SM", "action":"turnOn"})
        # TODO: DNS bootstrap Test ONLY 
        enqueue({"SM":"USER_SM", "action":"recvAck"})

    elif ROLE == "DRIVER":
        pass
    elif ROLE == "GSN":
        GSNStates.initialize()
        DISPATCHERMAP["GSN_SM"] = GSNStates
        
        # turnOn the machine
        enqueue({"SM":"GSN_SM", "action":"turnOn"})

# request by GUI app to find the nearest bus
# maybe can move this function to gui
def user_request(routeNo, direction, destination):
    message = {
               "SM" : "USER_SM",
               "action" : "request",
               "route" : routeNo,
               "direction" : direction,
               "destination" : destination
               }
    enqueue(message)

# enqueue the message into buffer for dispatch
def enqueue(message):
    global DISPATCH_QUEUE
    DISPATCH_QUEUE.append(message)

# offer message to state machine
def dispatch(message):
    if not message["SM"] in DISPATCHERMAP:
        LOGGER.info("Target state machine does NOT exist or closed")
    else:
        LOGGER.info("Dispatch message [%s]" % message)
        DISPATCHERMAP[message["SM"]].offerMsg(message)

# Test Only
if __name__ == '__main__':
    #name = sys.argv[1]
    #role = sys.argv[2]
    name = "alice"
    role = "USER"

    initialize("../testFile.txt", name, role)
    user_request("123", "north", "center ave")

