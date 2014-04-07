'''
Created on Apr 5, 2014

@author: Terry Li
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.RSNAction as RSNAction
import comm.MessagePasser as MessagePasser

logging.basicConfig()
LOGGER = logging.getLogger("RSNStateMachine")
LOGGER.setLevel(logging.DEBUG)

RSN_SM = None

BUS_TABLE = {}

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.turnOn:
            # TODO: do something about boot-strap
            # TODO: ping DNS
            # TODO: ping GNS
            return RSNSM.Init_Waiting
        else:
            # remain off
            return RSNSM.Off
    
class State_Init_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: Connecting to GSN")

    def __str__(self): 
        return "State_Init"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.recvGSNAck:
            # TODO: received the group info from GSN
            # TODO: store the group info
            return RSNSM.Ready
        elif action == RSNAction.timeout:
            # TODO: re-ping
            return RSNSM.Init_Waiting
        elif action == RSNAction.turnOff:
            # TODO: do something to shut-down
            return RSNSM.Off
        else:
            # for other illegal action
            assert 0, "Init: invalid action: %s" % str(input)


class State_Ready(State):
    def run(self):
        LOGGER.info("Ready for request")

    def __str__(self): 
        return "State_Ready"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.recvLocReq:
            # TODO: lookup the queried bus location and
            # TODO: response to user directly
            LOGGER.info("received location request: %s" % input)
            response_message = {
                               "SM" : "USER_SM",
                               "action" : "recvRes",
                               "location" : (1, 1), # location should be fetched from table
                               "bus_id" : 1
                               }
            # TODO: TEST ONLY; gsn should be modified
            MessagePasser.normalSend("user", response_message)
            
            return RSNSM.Ready
        elif action == RSNAction.recvDriverLoc:
            # TODO: update local cache
            return RSNSM.Ready
        elif action == RSNAction.turnOff:
            # TODO: do something to shut-down
            return RSNSM.Off
        else:
            # for other illegal action
            assert 0, "Ready: invalid action: %s" % str(input)


class RSNSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, RSNSM.Off)
        
    def run(self, input):
        self.currentState = self.currentState.next(input)
        self.currentState.run()
        
    def runAll(self, inputs):
        for input in inputs:
            self.run(input)
            
    def state(self):
        return self.currentState

def initialize():
    global RSN_SM
    RSN_SM = RSNSM()

def offerMsg(message):
    global RSN_SM
    if message["SM"] == "RSN_SM":
        RSN_SM.run(message)
        
def offerMsgs(messages):
    for message in messages:
        offerMsg(message)

RSNSM.Off = State_Off()
RSNSM.Init = State_Init_Waiting()
RSNSM.Ready = State_Ready()


# Test Only
if __name__ == '__main__':
    initialize()
    message1 = {
               "SM" : "RSN_SM",
               "action" : "turnOn"
               }
    message2 = {
               "SM" : "RSN_SM",
               "action" : "recvGNSAck"
               }
    #offerMsg(message1)
    offerMsgs([message1, message2])
