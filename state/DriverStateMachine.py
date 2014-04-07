'''
Created on Apr 5, 2014

@author: Terry Li
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.DriverAction as DriverAction
import comm.MessagePasser as MessagePasser

import socket

logging.basicConfig()
LOGGER = logging.getLogger("DriverStateMachine")
LOGGER.setLevel(logging.DEBUG)

DRIVER_SM = None

ROUTE_NO = -1
DIRECTION = None
BUS_ID = 0
LOCATION = (0, 0)

RSN_ADDR = None

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.turnOn:
            # TODO: do something about boot-strap
            # TODO: DNS query, need to read this name from config.
            # gsn_ip = socket.gethostbyname('ece.cmu.edu')
            gsn_ip = socket.gethostbyname('localhost')
            gsn_port = 20000  # pre-configured
            
            # TODO: ping GSN
            global ROUTE_NO, DIRECTION, BUS_ID
            ROUTE_NO = input["route"]
            DIRECTION = input["direction"]
            BUS_ID = input["bus_id"]
            add_message = {
                           "SM" : "GSN_SM",
                            "action" : "recvBusReq"
                           }
            # TODO: should use real gsn 
            MessagePasser.normalSend("gsn", add_message)
            
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
            global RSN_ADDR, ROUTE_NO, DIRECTION, BUS_ID, LOCATION
            # TODO: get RSN addr from the input
            RSN_ADDR["ip"] = input["rsn_ip"]
            RSN_ADDR["port"] = input["rsn_port"]
            
            # TODO: ping RSN to add into the group
            add_message = {
                           "SM" : "GSN_SM",
                            "action" : "recvBusChange",
                            "type" : "add",
                            "route" : ROUTE_NO,
                            "direction" : DIRECTION,
                            "bus_id" : BUS_ID,
                            "location" : LOCATION
                           }
            
            # TODO: should use real rsn
            MessagePasser.normalSend("rsn", add_message)
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
            # Qian: it is recorded in previous stage
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
            global ROUTE_NO, DIRECTION, LOCATION
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
            MessagePasser.normalSend("rsn", loc_message)
            
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
