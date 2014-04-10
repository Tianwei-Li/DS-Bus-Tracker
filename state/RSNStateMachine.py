'''
Created on Apr 5, 2014

@author: Terry Li
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.RSNAction as RSNAction
import comm.MessagePasser as MessagePasser
from util.Addr import Addr
import socket

logging.basicConfig()
LOGGER = logging.getLogger("RSNStateMachine")
LOGGER.setLevel(logging.DEBUG)

RSN_SM = None

GROUP_MEMBER = None
BUS_TABLE = {}

ROUTE_NO = None

GSN_ADDR = None
LOCAL_ADDR = None

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")

    def __str__(self): 
        return "State_Off"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.turnOn:
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
            #GROUP_MEMBER = input["group_member"]
            #BUS_TABLE = input["bus_table"]
            global GSN_ADDR, LOCAL_ADDR
            gsnIp = socket.gethostbyname('localhost')
            gsnPort = 40000  # pre-configured
            GSN_ADDR = Addr(gsnIp, gsnPort)
            
            LOCAL_ADDR = Addr(input["localIP"], input["localPort"])

            return RSNSM.Idle
        else:
            # remain off
            return RSNSM.Off
    
class State_Idle(State):
    def run(self):
        LOGGER.info("Idle: waiting for assignment")

    def __str__(self): 
        return "State_Idle"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.recvRSNAssign:
            # TODO: received the group info from GSN
            # TODO: store the group info
            
            global LOCAL_ADDR, ROUTE_NO, GROUP_MEMBER
            ROUTE_NO = input["route"]
            GROUP_MEMBER = input["groupMember"]

            # if the RSN is the Driver itself, send a recvRSNAck to driver role
            if input["type"] == "self":
                rsn_ack = {
                           "SM" : "DRIVER_SM",
                           "action" : "recvRSNAck",
                           "route" : ROUTE_NO,
                           "rsnIP" : LOCAL_ADDR.ip,
                           "rsnPort" : LOCAL_ADDR.port
                           }
                MessagePasser.directSend(input["original"]["driverIp"], input["original"]["driverPort"], rsn_ack)
            return RSNSM.Ready
        elif action == RSNAction.timeout:
            # TODO: re-ping
            # Terry: seems no need to re-ping gsn
            return RSNSM.Idle
        elif action == RSNAction.turnOff:
            # TODO: do something to shut-down
            return RSNSM.Off
        else:
            # for other illegal action
            assert 0, "Idle: invalid action: %s" % str(input)


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
                                "busId" : "alice",
                                "original" : input["original"]
                               }

            MessagePasser.directSend(input["original"]["userIP"], input["original"]["userPort"], response_message)
            
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
RSNSM.Idle = State_Idle()
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
