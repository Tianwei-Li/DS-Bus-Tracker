'''
Created on Apr 3, 2014

@author: Qian Mao
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.UserAction as UserAction

logging.basicConfig()
LOGGER = logging.getLogger("UserStateMachine")
LOGGER.setLevel(logging.DEBUG)

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def next(self, input):
        if input == UserAction.turnOn:
            # TODO: do something about boot-strap
            # TODO: ping GSN
            return UserSM.Init_Waiting
        else:
            # remain off
            return UserSM.Off
    
class State_Init_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: Connecting to GSN")

    def next(self, input):
        if input == UserAction.recvAck:
            # TODO: do something
            return UserSM.Ready
        elif input == UserAction.timeout:
            # TODO: re-ping
            return UserSM.Init_Waiting
        elif input == UserAction.turnOff:
            # TODO: do something to shut-down
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Init_Waiting: invalid action"

    
class State_Ready(State):
    def run(self):
        LOGGER.info("Ready for request")

    def next(self, input):
        if input == UserAction.request:
            # TODO: send a request to GSN
            return UserSM.Req_Waiting
        elif input == UserAction.turnOff:
            # TODO: do something to shut-down
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Ready: invalid action"


class State_Req_Waiting(State):
    def run(self):
        LOGGER.info("Waiting: requesting")

    def next(self, input):
        if input == UserAction.recvRes:
            # TODO: return response to GUI
            return UserSM.Ready
        elif input == UserAction.timeout:
            # TODO: re-send request if under threshold
            return UserSM.Req_Waiting
        elif input == UserAction.turnOff:
            # TODO: do something to shut-down
            return UserSM.Off
        else:
            # for other illegal action
            assert 0, "Req_Waiting: invalid action"


    
class UserSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, UserSM.Off)

UserSM.Off = State_Off()
UserSM.Init_Waiting = State_Init_Waiting()
UserSM.Ready = State_Ready()
UserSM.Req_Waiting = State_Req_Waiting()



# Test only
if __name__ == '__main__':
    UserSM().runAll(
                    [UserAction.turnOn, 
                     UserAction.timeout, 
                     UserAction.recvAck, 
                     UserAction.request, 
                     UserAction.recvRes, 
                     UserAction.turnOff])