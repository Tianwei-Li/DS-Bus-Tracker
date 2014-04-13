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

RESPONSE_QUE = collections.deque()

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
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

    def __str__(self): 
        return "State_Ready"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.request:
            global LOCAL_ADDR, GSN_ADDR, USER_ID, REQUEST_SEQ
            # TODO: send a request to GSN
            LOGGER.info("send user request: %s" % input)
            request_message = {
                               "SM" : "GSN_SM",
                               "action" : "recvUserReq",
                               "requestId" : USER_ID + str(REQUEST_SEQ),
                               "userId" : USER_ID,
                               "route" : input["route"],
                               "direction" : input["direction"],
                               "destination" : input["destination"],
                               "location" : input["location"],
                               "userIP" : LOCAL_ADDR.ip,
                               "userPort" : LOCAL_ADDR.port
                               }
            # TODO: TEST ONLY; gsn should be modified
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, request_message)
            return UserSM.Req_Waiting
        elif action == UserAction.turnOff:
            # TODO: do something to shut-down
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Ready: invalid action: %s" % str(input)


class State_Req_Waiting(State):
    def run(self):
        LOGGER.info("Req_Waiting: requesting")

    def __str__(self): 
        return "State_Req_Waiting"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.recvRes:
            # TODO: return response to GUI
            global RESPONSE_QUE
            LOGGER.info("receive response from RSN")
            RESPONSE_QUE.append(input)
            return UserSM.Ready
        elif action == UserAction.timeout:
            # TODO: re-send request if under threshold
            return UserSM.Req_Waiting
        elif action == UserAction.turnOff:
            # TODO: do something to shut-down
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Req_Waiting: invalid action: %s" % str(input)


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
    global USER_SM
    USER_SM = UserSM()

def offerMsg(message):
    global USER_SM
    if message["SM"] == "USER_SM":
        USER_SM.run(message)
        
def offerMsgs(messages):
    for message in messages:
        offerMsg(message)

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
