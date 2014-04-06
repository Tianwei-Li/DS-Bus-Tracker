'''
Created on Apr 5, 2014

@author: Qian Mao
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.GSNAction as GSNAction

logging.basicConfig()
LOGGER = logging.getLogger("GSNStateMachine")
LOGGER.setLevel(logging.DEBUG)

GSN_SM = None

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")
        
    def __str__(self): 
        return "State_Off"

    def next(self, input):
        if input == GSNAction.turnOn:
            # do something about boot-strap
            # 
            return GSNSM.Ready
        else:
            # remain off
            return GSNSM.Off
    
class State_Ready(State):
    def run(self):
        LOGGER.info("Ready")
        
    def __str__(self): 
        return "State_Ready"

    def next(self, input):
        # TODO: other input option
        if input == GSNAction.recvUserReq:
            # TODO: forward user request to responding RSN
            return GSNSM.Ready
        elif input == GSNAction.recvBusReq:
            # TODO: update route table and forward user request to responding RSN
            return GSNSM.Ready
        elif input == GSNAction.turnOff:
            # TODO: do something to shut-down
            return GSNSM.Off


    
class GSNSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, GSNSM.Off)
        
    def run(self, input):
        self.currentState = self.currentState.next(map(GSNAction.GSNAction, [input])[0])
        self.currentState.run()
        
    def runAll(self, inputs):
        actions = map(GSNAction.GSNAction, inputs)
        for i in actions:
            self.currentState = self.currentState.next(i)
            self.currentState.run()
            
    def state(self):
        return self.currentState
        
def initialize():
    global GSN_SM
    GSN_SM = GSNSM()

def offerMsg(message):
    global GSN_SM
    if message["SM"] == "GSN_SM":
        GSN_SM.run(message["action"])
        
def offerMsgs(messages):
    for message in messages:
        offerMsg(message)

GSNSM.Off = State_Off()
GSNSM.Ready = State_Ready()