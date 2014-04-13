'''
Created on Apr 2, 2014

@author: Qian Mao
'''
import sys
sys.path += ['../']

import comm.MessagePasser as MessagePasser
import state.UserStateMachine as UserStateMachine
import state.DriverStateMachine as DriverStateMachine
import state.RSNStateMachine as RSNStateMachine
import state.GSNStateMachine as GSNStateMachine
import time
import collections
import threading
import logging
import socket


logging.basicConfig()
LOGGER = logging.getLogger("Host")
LOGGER.setLevel(logging.DEBUG)

LOCALNAME = None
ROLE = None
STATE = None
USERSM = None
DRIVERSM = None

GSN_ADDR = None
SELF_ADDR = None

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
def initialize(conf, localName, role, id, localIP, localPort):
    global LOCALNAME, ROLE, USERSM, SELF_ADDR
    LOCALNAME = localName
    ROLE = role
    # TODO: conf might be changed
    MessagePasser.initialize(conf, localName)
    SELF_ADDR = socket.gethostbyname(socket.getfqdn())
    
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
        UserStateMachine.initialize()
        DISPATCHERMAP["USER_SM"] = UserStateMachine
        
        # turnOn the machine
        enqueue({"SM":"USER_SM", "action":"turnOn", "userId":id, "localIP":localIP, "localPort":localPort})

    elif ROLE == "DRIVER":
        DriverStateMachine.initialize()
        DISPATCHERMAP["DRIVER_SM"] = DriverStateMachine
        
        RSNStateMachine.initialize()
        DISPATCHERMAP["RSN_SM"] = RSNStateMachine
        
        # turnOn the machine
        enqueue({"SM":"DRIVER_SM", "action":"turnOn", "busId":id, "localIP":localIP, "localPort":localPort})
        enqueue({"SM":"RSN_SM", "action":"turnOn", "rsnId":id, "localIP":localIP, "localPort":localPort})
        
        
    elif ROLE == "GSN":
        GSNStateMachine.initialize()
        DISPATCHERMAP["GSN_SM"] = GSNStateMachine
        
        # turnOn the machine
        enqueue({"SM":"GSN_SM", "action":"turnOn", "gsnId":id, "localIP":localIP, "localPort":localPort})
        
def autoInitialize(ip, port, localName, role, routNo, interval):
    global LOCALNAME, ROLE, USERSM
    LOCALNAME = localName
    ROLE = role
    MessagePasser.autoInitialize(ip, port, localName)
    
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
        UserStateMachine.initialize()
        DISPATCHERMAP["USER_SM"] = UserStateMachine
        
        # turnOn the machine
        enqueue({"SM":"USER_SM", "action":"turnOn"})
        # TODO: DNS bootstrap Test ONLY 
        enqueue({"SM":"USER_SM", "action":"recvAck"})
        
        # send bus query periodically
        while True:
            time.sleep(interval)
            # TODO: send query message
            

    elif ROLE == "DRIVER":
        DriverStateMachine.initialize()
        DISPATCHERMAP["DRIVER_SM"] = DriverStateMachine
        
        # turnOn the machine
        enqueue({"SM":"DRIVER_SM", "action":"turnOn"})
        
    elif ROLE == "GSN":
        GSNStateMachine.initialize()
        DISPATCHERMAP["GSN_SM"] = GSNStateMachine
        
        # turnOn the machine
        enqueue({"SM":"GSN_SM", "action":"turnOn"})

# request by GUI app to find the nearest bus
# maybe can move this function to gui
def user_request(routeNo, direction, destination, location):
    message = {
               "SM" : "USER_SM",
               "action" : "request",
               "route" : routeNo,
               "direction" : direction,
               "destination" : destination,
               "location" : location    # user current location
               }
    enqueue(message)

# enqueue the message into buffer for dispatch
def enqueue(message):
    global DISPATCH_QUEUE
    DISPATCH_QUEUE.append(message)

# offer message to state machine
def dispatch(message):
    if not message["SM"] in DISPATCHERMAP:
        LOGGER.info("Target state machine does NOT exist or closed: %s" % message)
    else:
        LOGGER.info("Dispatch message [%s]" % message)
        DISPATCHERMAP[message["SM"]].offerMsg(message)

# Test Only
def gsnConsole():
    while True:
        try:
            print "---------GSN--------\n1. turn on\n2. turn off\n--------------------"
            input = int(raw_input('Input:'))
            if input == 1:
                enqueue({"SM":"GSN_SM", "action":"turnOn", "gsnId":"gsn_1", "localIP":"127.0.0.1", "localPort":40000})
            elif input == 2:
                enqueue({"SM":"GSN_SM", "action":"turnOff"})
            else:
                raise Exception("please enter number [1-2]")
        except ValueError:
            print "Not a number"
        except Exception as e:
            print e

# Test Only
def driverConsole():
    while True:
        try:
            print "-------DRIVER-------\n1. turn on\n2. start\n3. turn off\n--------------------"
            input = int(raw_input('Input:'))
            if input == 1:
                enqueue({"SM":"DRIVER_SM", "action":"turnOn", "busId":"bus_71A_1", "localIP":"127.0.0.1", "localPort":41000})
            elif input == 2:
                enqueue({"SM":"DRIVER_SM", "action":"start", "route":"71A", "direction":"north", "location":(0,0)})
            elif input == 3:
                enqueue({"SM":"DRIVER_SM", "action":"turnOff"})

            else:
                raise Exception("please enter number [1-3]")
        except ValueError:
            print "Not a number"
        except Exception as e:
            print e

# Test Only
def userConsole():
    while True:
        try:
            print "--------USER--------\n1. turn on\n2. request\n3. turn off\n--------------------"
            input = int(raw_input('Input:'))
            if input == 1:
                enqueue({"SM":"USER_SM", "action":"turnOn", "userId":"user_alice", "localIP":"127.0.0.1", "localPort":30000})
            elif input == 2:
                enqueue({"SM":"USER_SM", "action":"request", "route":"71A", "direction":"north", "destination":(1,1), "location":(0,1)})
            elif input == 3:
                enqueue({"SM":"USER_SM", "action":"turnOff"})

            else:
                raise Exception("please enter number [1-3]")
        except ValueError:
            print "Not a number"
        except Exception as e:
            print e

# Test Only
if __name__ == '__main__':
    '''
    ip = sys.argv[1]
    port = sys.argv[2]
    localName = sys.argv[3]
    role = sys.argv[4]
    routNo = sys.argv[5]
    interval = sys.argv[6]
    '''
    #initialize("../testFile.txt", name, role)
    #autoInitialize(ip, int(port), localName, role, routNo, interval)
    #user_request("123", "north", "center ave")

    #print socket.gethostbyname('ece.cmu.edu')
    #print socket.gethostbyname(socket.getfqdn())
    '''
    localName = sys.argv[1]
    SM = sys.argv[2]
    id = sys.argv[3]
    localIP = sys.argv[4]
    localPort = sys.argv[5]

    #initialize("../testFile.txt", "gsn", "GSN", "gsn_1", "127.0.0.1", 40000)
    initialize("../testFile.txt", localName, SM, id, localIP, localPort)
    '''
    
    role = None
    
    while True:
        try:
            print "--------------------\n1. launch GSN\n2. launch DRIVER_1\n3. launch DRIVER_2\n4. launch a USER\n--------------------"
            input = int(raw_input('Input:'))
            if input == 1:
                role = "GSN"
                initialize("../testFile.txt", "gsn", "GSN", "gsn_1", "127.0.0.1", 40000)
                gsnConsole()
            elif input == 2:
                role = "DRIVER"
                initialize("../testFile.txt", "driver1", "DRIVER", "bus_71A_1", "127.0.0.1", 41000)
                driverConsole()
            elif input == 3:
                role = "DRIVER"
                initialize("../testFile.txt", "driver2", "DRIVER", "bus_71A_2", "127.0.0.1", 42000)
                driverConsole()
            elif input == 4:
                role = "USER"
                initialize("../testFile.txt", "user", "USER", "user_alice", "127.0.0.1", 30000)
                userConsole()
            else:
                raise Exception("please enter number [1-4]")
        except ValueError:
            print "Not a number"
        except Exception as e:
            print e


