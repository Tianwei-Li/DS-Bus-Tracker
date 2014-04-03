'''
Created on Apr 3, 2014

@author: Qian Mao
'''

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
        if input == UserAction.turnOn:
            # do something about boot-strap
            # ping GSN
            return UserSM.Init_Waiting
        else:
            # remain off
            return UserSM.Off
    
class State_Init_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: Connecting to GSN")

    def next(self, input):
        if input == UserAction.recvAck:
            # do something
            return UserSM.Ready
        elif input == UserAction.timeout:
            # re-ping
            return UserSM.Init_Waiting
        elif input == UserAction.turnOff:
            # do something to shut-dowm
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Init_Waiting: invalid action"

    
class State_Ready(State):
    def run(self):
        LOGGER.info("Ready for request")

    def next(self, input):
        if input == UserAction.request:
            # send a request to GSN
            pass
        else:
            pass

        #return MouseTrap.waiting

class State_Req_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: requesting")

    def next(self, input):
        if input == UserAction.recvRes:
            # send a request to GSN
            pass
        else:
            pass


    
class UserSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, UserSM.Off)

UserSM.Off = State_Off()
UserSM.Init_Waiting = State_Init_Waiting()
UserSM.Ready = State_Ready()
