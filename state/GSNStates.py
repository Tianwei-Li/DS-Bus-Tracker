import logging
from state.State import State
from state.StateMachine import StateMachine
import action.UserAction as UserAction

LOGGER = logging.getLogger("UserStateMachine")
LOGGER.setLevel(logging.DEBUG)

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def next(self, input):
        if input == GSNAction.turnOn:
            # do something about boot-strap
            # 
            return GSNSM.Init_Waiting
        else:
            # remain off
            return GSNSM.Off
    
class State_Init_Waiting(State):
    

    
class State_Ready(State):
    

class State_Req_Waiting(State):
    


    
class GSNSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, GSNSM.Off)

GSNSM.Off = State_Off()
GSNSM.Init_Waiting = State_Init_Waiting()
GSNSM.Ready = State_Ready()