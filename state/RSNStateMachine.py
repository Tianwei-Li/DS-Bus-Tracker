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

GROUP_MEMBER = []
BUS_TABLE = {}

ROUTE_NO = None

GSN_ADDR = None

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.recvRSNAssign:
            # TODO: do something about boot-strap
            # TODO: ping GSN
            # Qian: turnOn is called by host, thus, it is not necessary to make a DNS query.
            # just pass it within input
            # RSN can be set by:
            # 1. There is one bus asking for adding but there is no RSN yet (that bus is the first one in its route)
            # 2. The previous RSN is lost
            # for situation 1, the driver state machine will be hung up because he needs to wait for the initialization of RSN state machine
            # In situation 2, the GSN will send a backup group info to the new RSN. (Backup is not necessary for situation 1)
            
            
            # Terry: when a rsn turn on, it means gsn sent a message to bus to indicate it to be a rsn
            # Terry: the message should include the route and group info
            GROUP_MEMBER = input["group_member"]
            BUS_TABLE = input["bus_table"]
            
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
            GROUP_MEMBER = input["group_member"]
            return RSNSM.Ready
        elif action == RSNAction.timeout:
            # TODO: re-ping
            # Terry: seems no need to re-ping gsn
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
        elif action == RSNAction.askBusLoc:
            # periodically ask each buses' location
            # TODO: triggered by host timer
            global GROUP_MEMBER
            req_loc_message = {
                               "SM" : "DRIVER_SM",
                               "action" : "recvLocReq"
                               #"route" : ROUTE_NO,
                               }
            #MessagePasser.multicast(GROUP_MEMBER, req_loc_message)
            # TODO: replace the code below with a multicast version
            for member in GROUP_MEMBER:
                MessagePasser.normalSend(member, req_loc_message)
                
            return RSNSM.Ready
        elif action == RSNAction.recvDriverLoc:
            # TODO: update local cache
            global BUS_TABLE, ROUTE_NO

            if input["route"] == ROUTE_NO:
                BUS_TABLE[input["bus_id"]] = {
                                              "direction" : input["direction"],
                                              "location" : input["location"]
                                              }
            
            return RSNSM.Ready
        elif action == RSNAction.recvBusChange:
            # TODO: add or remove a bus from current group
            global GROUP_MEMBER, BUS_TABLE, ROUTE_NO
            
            if input["route"] == ROUTE_NO:
                if input["type"] == "add":
                    if not input["bus_id"] in GROUP_MEMBER:
                        GROUP_MEMBER.append(input["bus_id"])
                        BUS_TABLE[input["bus_id"]] = {
                                                      "direction" : input["direction"],
                                                      "location" : input["location"],
                                                      "last_update" : 0 # TODO: use local time stamp
                                                      }
                elif input["type"] == "remove":
                    if input["bus_id"] in GROUP_MEMBER:
                        GROUP_MEMBER.remove(input["bus_id"])
                        BUS_TABLE.pop(input["bus_id"])
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
