'''
Created on Apr 5, 2014

@author: Terry Li
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.DriverAction as DriverAction
import comm.MessagePasser as MessagePasser
from util.Addr import Addr

import socket

logging.basicConfig()
LOGGER = logging.getLogger("DriverStateMachine")
LOGGER.setLevel(logging.DEBUG)

DRIVER_SM = None

ROUTE_NO = -1
DIRECTION = None
BUS_ID = 0
LOCATION = (0, 0)    # should be updated by some other module

LOCAL_ADDR = None
GSN_ADDR = None
RSN_ADDR = None

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.turnOn:
            global ROUTE_NO, DIRECTION, BUS_ID, LOCAL_ADDR, GSN_ADDR

            # TODO: do something about boot-strap
            # TODO: DNS query, need to read this name from config.
            # gsn_ip = socket.gethostbyname('ece.cmu.edu')
            gsnIp = socket.gethostbyname('localhost')
            gsnPort = 40000  # pre-configured
            GSN_ADDR = Addr(gsnIp, gsnPort)
            
            LOCAL_ADDR = Addr(input["localIP"], input["localPort"])
            BUS_ID = input["busId"]            
            
            return DriverSM.Idle
        else:
            # remain off
            return DriverSM.Off

class State_Idle(State):
    def run(self):
        LOGGER.info("Idle")

    def __str__(self): 
        return "State_Idle"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.start:
            global LOCAL_ADDR, RSN_ADDR, ROUTE_NO, DIRECTION, BUS_ID, LOCATION
            
            ROUTE_NO = input["route"]
            DIRECTION = input["direction"]
            LOCATION = input["location"]
            
            # TODO: ping RSN to add into the group
            add_message = {
                           "SM" : "GSN_SM",
                           "action" : "recvBusReq",
                           "type" : "add",
                           "route" : ROUTE_NO,
                           "direction" : LOCATION,
                           "busId" : BUS_ID,
                           "location" : LOCATION, 
                           "driverIp" : LOCAL_ADDR.ip,
                           "driverPort" : LOCAL_ADDR.port
                           }
            # TODO: should use real gsn 
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, add_message)
            
            return DriverSM.Init_Waiting
        elif action == DriverAction.timeout:
            # TODO: re-ping
            return DriverSM.Idle
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            return DriverSM.Off
        else:
            # for other illegal action
            assert 0, "Idle: invalid action: %s" % str(input)
            
            
class State_Init_Waiting(State):
    def run(self):
        LOGGER.info("Init_Waiting")

    def __str__(self): 
        return "State_Init"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.recvRSNAck:
            global MYSELF_ADDR, RSN_ADDR, ROUTE_NO, DIRECTION, BUS_ID, LOCATION

            # if the response route number doesn't match
            if input["route"] != ROUTE_NO:
                return DriverSM.Init_Waiting
            
            RSN_ADDR = Addr(input["rsnIP"], input["rsnPort"])

            return DriverSM.Ready
        elif action == DriverAction.timeout:
            # TODO: re-ping
            return DriverSM.Init_Waiting
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            return DriverSM.Off
        else:
            # for other illegal action
            assert 0, "Init_Waiting: invalid action: %s" % str(input)


class State_Ready(State):
    def run(self):
        LOGGER.info("Ready")

    def __str__(self): 
        return "State_Ready"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.recvLocReq:
            # TODO: response the current location
            # check if the rsn is my RSN, route matched?
            global ROUTE_NO, DIRECTION, LOCATION, RSN_ADDR
            LOGGER.info("received RSN location request: %s" % input)
            loc_message = {
                           "SM" : "RSN_SM",
                           "action" : "recvDriverLoc",
                           "route" : ROUTE_NO,
                           "direction" : DIRECTION,
                           "bus_id" : BUS_ID,
                           "location" : LOCATION,
                           }
            # TODO: TEST ONLY; rsn should be modified
            MessagePasser.directSend(RSN_ADDR.ip, RSN_ADDR.port, loc_message)
            
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
DriverSM.Idle = State_Idle()
DriverSM.Init_Waiting = State_Init_Waiting()
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
