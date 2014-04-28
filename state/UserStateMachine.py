'''
Created on Apr 3, 2014

@author: Qian Mao
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.UserAction as UserAction
import comm.MessagePasser as MessagePasser
from util.Addr import Addr
from util.WatchDog import Watchdog
import socket
import collections

logging.basicConfig()
LOGGER = logging.getLogger("UserStateMachine")
LOGGER.setLevel(logging.DEBUG)

USER_SM = None

GSN_ADDR = None
LOCAL_ADDR = None

USER_ID = None
REQUEST_SEQ =0

LAST_REQ = None
LAST_RESPONSE = None
ARRIVE_TIME = -1
IS_REPORTED = False

WAITING_REQ_LIST = []
RESPONSE_QUE = collections.deque()

WATCHDOG = None

# func passed into watchdog
def watchdogFunc():
    LOGGER.info("reqTimeout")
    reqTimeout_message = {
                          "SM" : "USER_SM",
                          "action" : "reqTimeout",
                          }
    offerMsg(reqTimeout_message)
    
class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __repr__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.turnOn:
            global LOCAL_ADDR, GSN_ADDR, USER_ID
            # TODO: do something about boot-strap
            # TODO: ping DNS
            LOCAL_ADDR = Addr(input["localIP"], input["localPort"])
            gsnIp = socket.gethostbyname('localhost')
            gsnPort = 40000  # pre-configured
            GSN_ADDR = Addr(gsnIp, gsnPort)
            USER_ID = input["userId"]
            return UserSM.Ready
        else:
            # remain off
            return UserSM.Off
    
class State_Ready(State):
    def run(self):
        LOGGER.info("Ready")

    def __repr__(self): 
        return "State_Ready"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.request:
            global LOCAL_ADDR, GSN_ADDR, USER_ID, REQUEST_SEQ, WAITING_REQ_LIST, LAST_REQ, WATCHDOG, LAST_RESPONSE, IS_REPORTED
            # TODO: send a request to GSN
            LOGGER.info("send user request: %s" % input)
            REQUEST_SEQ = REQUEST_SEQ + 1
            requestId = USER_ID + str(REQUEST_SEQ)
            
            request_message = {
                               "SM" : "GSN_SM",
                               "action" : "recvUserReq",
                               "requestId" : requestId,
                               "userId" : USER_ID,
                               "route" : input["route"],
                               "direction" : input["direction"],
                               "destination" : input["destination"],
                               "location" : input["location"],
                               "userIP" : LOCAL_ADDR.ip,
                               "userPort" : LOCAL_ADDR.port
                               }
            
            LAST_REQ = request_message
            LAST_RESPONSE = None
            IS_REPORTED = False

            # TODO: TEST ONLY; gsn should be modified
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, request_message)
            WAITING_REQ_LIST.append(requestId)
            
            WATCHDOG.startWatchdog()
            
            return UserSM.Req_Waiting
        elif action == UserAction.turnOff:
            # TODO: do something to shut-down
            global WATCHDOG
            WATCHDOG.stopWatchdog()
            return UserSM.Off
        else:
            # for other illegal action
            # assert 0, "Ready: invalid action: %s" % str(input)
            pass


class State_Req_Waiting(State):
    def run(self):
        LOGGER.info("Req_Waiting: requesting")

    def __repr__(self): 
        return "State_Req_Waiting"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.recvRes:
            # TODO: return response to GUI
            global RESPONSE_QUE, WAITING_REQ_LIST, WATCHDOG, LAST_RESPONSE, LAST_REQ, ARRIVE_TIME
            LOGGER.info("receive response from RSN %s" % input)
            
            WATCHDOG.stopWatchdog()

            if str(input["original"]["requestId"]) in WAITING_REQ_LIST:
                RESPONSE_QUE.append(input)
                # if the last res is matched with last req, calculate arrive time
                if input["original"]["requestId"] == LAST_REQ["requestId"]:
                    if input["location"] == None:
                        diff = -1
                    else:
                        diff = int(LAST_REQ["location"]) - int(input["location"])
                    ARRIVE_TIME = diff
                    LAST_RESPONSE = input
                    IS_REPORTED = False
                
            return UserSM.Ready
        elif action == UserAction.reqTimeout:
            # TODO: re-send request if over threshold
            global LAST_REQ, WATCHDOG
            
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, LAST_REQ)
            
            WATCHDOG.petWatchdog()
            return UserSM.Req_Waiting
        elif action == UserAction.turnOff:
            # TODO: do something to shut-down
            global WATCHDOG
            WATCHDOG.stopWatchdog()
            return UserSM.Off
        else:
            # for other illegal action
            # assert 0, "Req_Waiting: invalid action: %s" % str(input)
            pass


class UserSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, UserSM.Off)
        
    def run(self, input):
        self.currentState = self.currentState.next(input)
        self.currentState.run()
        
    def runAll(self, inputs):
        for input in inputs:
            self.run(input)
            
    def state(self):
        return self.currentState

def initialize():
    global USER_SM, WATCHDOG
    USER_SM = UserSM()
    WATCHDOG = Watchdog(15, watchdogFunc)


def offerMsg(message):
    global USER_SM
    if message["SM"] == "USER_SM":
        USER_SM.run(message)
        
def offerMsgs(messages):
    for message in messages:
        offerMsg(message)

def state():
    global USER_SM
    return str(USER_SM.currentState)

UserSM.Off = State_Off()
#UserSM.Init_Waiting = State_Init_Waiting()
UserSM.Ready = State_Ready()
UserSM.Req_Waiting = State_Req_Waiting()


# Test Only
if __name__ == '__main__':
    initialize()
    message1 = {
               "SM" : "USER_SM",
               "action" : "turnOn"
               }
    message2 = {
               "SM" : "USER_SM",
               "action" : "recvAck"
               }
    #offerMsg(message1)
    offerMsgs([message1, message2])
