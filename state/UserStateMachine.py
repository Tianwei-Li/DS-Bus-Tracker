'''
Created on Apr 3, 2014

@author: Qian Mao
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.UserAction as UserAction
import comm.MessagePasser as MessagePasser

logging.basicConfig()
LOGGER = logging.getLogger("UserStateMachine")
LOGGER.setLevel(logging.DEBUG)

USER_SM = None

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.turnOn:
            # TODO: do something about boot-strap
            # TODO: ping DNS
            return UserSM.Init_Waiting
        else:
            # remain off
            return UserSM.Off
    
class State_Init_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: Connecting to GSN")

    def __str__(self): 
        return "State_Init_Waiting"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.recvAck:
            # TODO: do something
            return UserSM.Ready
        elif action == UserAction.timeout:
            # TODO: re-ping
            return UserSM.Init_Waiting
        elif action == UserAction.turnOff:
            # TODO: do something to shut-down
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Init_Waiting: invalid action: %s" % str(input)

    
class State_Ready(State):
    def run(self):
        LOGGER.info("Ready for request")

    def __str__(self): 
        return "State_Ready"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.request:
            # TODO: send a request to GSN
            LOGGER.info("send user request: %s" % input)
            request_message = {
                               "SM" : "GSN_SM",
                               "action" : "recvUserReq",
                               "route" : input["route"],
                               "direction" : input["direction"],
                               "destination" : input["destination"],
                               "userIP" : MessagePasser.localIP,
                               "userPort" : MessagePasser.localPort
                               }
            # TODO: TEST ONLY; gsn should be modified
            MessagePasser.normalSend("gsn", request_message)
            return UserSM.Req_Waiting
        elif action == UserAction.turnOff:
            # TODO: do something to shut-down
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Ready: invalid action: %s" % str(input)


class State_Req_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: requesting")

    def __str__(self): 
        return "State_Req_Waiting"
    
    def next(self, input):
        action = map(UserAction.UserAction, [input["action"]])[0]
        if action == UserAction.recvRes:
            # TODO: return response to GUI
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
UserSM.Init_Waiting = State_Init_Waiting()
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
