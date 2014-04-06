'''
Created on Apr 5, 2014

@author: Terry Li
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.DriverAction as DriverAction
import comm.MessagePasser as MessagePasser

logging.basicConfig()
LOGGER = logging.getLogger("DriverStateMachine")
LOGGER.setLevel(logging.DEBUG)

DRIVER_SM = None

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.turnOn:
            # TODO: do something about boot-strap
            # TODO: ping DNS
            # TODO: ping GNS
            return DriverSM.Init_Waiting
        else:
            # remain off
            return DriverSM.Off
    
class State_Init_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: Connecting to GSN")

    def __str__(self): 
        return "State_Init"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.recvGSNAck:
            # TODO: get RSN addr from the input
            # TODO: ping RSN to add into the group
            return DriverSM.Setup
        elif action == DriverAction.timeout:
            # TODO: re-ping
            return DriverSM.Init_Waiting
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            return DriverSM.Off
        else:
            # for other illegal action
            assert 0, "Init_Waiting: invalid action: %s" % str(input)


class State_Setup(State):
    def run(self):
        LOGGER.info("Setuping: Connecting to RSN")

    def __str__(self): 
        return "State_Setup"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.recvRSNAck:
            # TODO: record the RSN address
            return DriverSM.Ready
        elif action == DriverAction.timeout:
            # TODO: re-ping
            return DriverSM.Setup
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            return DriverSM.Off
        else:
            # for other illegal action
            assert 0, "Setup: invalid action: %s" % str(input)


class State_Ready(State):
    def run(self):
        LOGGER.info("Ready for request")

    def __str__(self): 
        return "State_Ready"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.recvLocReq:
            # TODO: response the current location
            LOGGER.info("received RSN location request: %s" % input)
            request_message = {
                               "SM" : "RSN_SM",
                               "action" : "recvRes",
                               "location" : (1, 1),
                               "bus_id" : 1
                               }
            # TODO: TEST ONLY; gsn should be modified
            MessagePasser.normalSend("rsn", request_message)
            
            return DriverSM.Ready
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            return DriverSM.Off
        else:
            # for other illegal action
            assert 0, "Ready: invalid action: %s" % str(input)


class DriverSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, DriverSM.Off)
        
    def run(self, input):
        self.currentState = self.currentState.next(input)
        self.currentState.run()
        
    def runAll(self, inputs):
        for input in inputs:
            self.run(input)
            
    def state(self):
        return self.currentState

def initialize():
    global DRIVER_SM
    DRIVER_SM = DriverSM()

def offerMsg(message):
    global DRIVER_SM
    if message["SM"] == "DRIVER_SM":
        DRIVER_SM.run(message)
        
def offerMsgs(messages):
    for message in messages:
        offerMsg(message)

DriverSM.Off = State_Off()
DriverSM.Init_Waiting = State_Init_Waiting()
DriverSM.Setup = State_Setup()
DriverSM.Ready = State_Ready()


# Test Only
if __name__ == '__main__':
    initialize()
    message1 = {
               "SM" : "DRIVER_SM",
               "action" : "turnOn"
               }
    message2 = {
               "SM" : "DRIVER_SM",
               "action" : "recvGNSAck"
               }
    #offerMsg(message1)
    offerMsgs([message1, message2])
