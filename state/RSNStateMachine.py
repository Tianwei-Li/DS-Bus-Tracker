'''
Created on Apr 5, 2014

@author: Terry Li, Qian Mao
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.RSNAction as RSNAction
import comm.MessagePasser as MessagePasser
from util.Addr import Addr
import socket
import threading
import time

logging.basicConfig()
LOGGER = logging.getLogger("RSNStateMachine")
LOGGER.setLevel(logging.DEBUG)

RSN_SM = None

GROUP_MEMBER = None

'''
key            values:
busId       direction,
            location,
            addr,
            last_update
'''
BUS_TABLE = {}


ROUTE_NO = None

GSN_ADDR = None
LOCAL_ADDR = None

TIMER_ON = None
TIMER_OFF = None
TIMER_THREAD = None

LOC_REQ_NO = 0

# Timer thread
def timerThread(timerOn, timerOff):
    while timerOn.wait():
        while not timerOff.wait(5):     # every 5 secs
            # send a askBusLoc to RSN_SM
            askBusLoc_message = {
                                 "SM" : "RSN_SM",
                                 "action" : "askBusLoc"
                                 }
            offerMsg(askBusLoc_message)

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
            global GSN_ADDR, LOCAL_ADDR, RSN_ID
            gsnIp = socket.gethostbyname('localhost')
            gsnPort = 40000  # pre-configured
            GSN_ADDR = Addr(gsnIp, gsnPort)
            
            LOCAL_ADDR = Addr(input["localIP"], input["localPort"])
            RSN_ID = input["rsnId"]
            
            LOC_REQ_NO = 0

            return RSNSM.Idle
        else:
            # remain off
            return RSNSM.Off
    
class State_Idle(State):
    def run(self):
        LOGGER.info("Idle")

    def __str__(self): 
        return "State_Idle"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.recvRSNAssign:
            # TODO: received the group info from GSN
            # TODO: store the group info
            
            global LOCAL_ADDR, ROUTE_NO, BUS_TABLE, TIMER_ON, TIMER_OFF
            ROUTE_NO = input["route"]

            # if the RSN is the Driver itself, send a recvRSNAck to driver role
            if input["type"] == "self":
                BUS_TABLE[input["original"]["busId"]] = {
                                             "direction" : input["original"]["direction"],
                                             "location" : input["original"]["location"],
                                             "addr" : Addr(input["original"]["busIP"], input["original"]["busPort"]),
                                             "last_update" : 0 # TODO: use local time stamp
                                             }
                
                rsn_ack = {
                           "SM" : "DRIVER_SM",
                           "action" : "recvRSNAck",
                           "route" : ROUTE_NO,
                           "rsnId" : RSN_ID,
                           "rsnIP" : LOCAL_ADDR.ip,
                           "rsnPort" : LOCAL_ADDR.port
                           }
                MessagePasser.directSend(input["original"]["busIP"], input["original"]["busPort"], rsn_ack)
            elif input["type"] == "normal":
                BUS_TABLE = input["busTable"]
                
                # notify each bus 
                global GROUP_MEMBER, RSN_ID, ROUTE_NO, LOCAL_ADDR, LOC_REQ_NO
                LOGGER.info("asking each bus' location %s" % BUS_TABLE.keys())
                LOC_REQ_NO = 0
                LOC_REQ_NO = LOC_REQ_NO + 1             # maybe overflow!!!
            
                req_loc_message = {
                                   "SM" : "DRIVER_SM",
                                   "action" : "recvLocReq",
                                   "requestNo" : LOC_REQ_NO,
                                   "rsnId" : RSN_ID,
                                   "route" : ROUTE_NO,
                                   "rsnIP" : LOCAL_ADDR.ip,
                                   "rsnPort" : LOCAL_ADDR.port
                                   }

                for member in BUS_TABLE:
                    MessagePasser.directSend(BUS_TABLE[member]["addr"].ip, BUS_TABLE[member]["addr"].port, req_loc_message)
                
                
            # unblock the timer thread
            TIMER_OFF.clear()
            TIMER_ON.set()
            
            return RSNSM.Ready
        elif action == RSNAction.timeout:
            # TODO: re-ping
            # Terry: seems no need to re-ping gsn
            return RSNSM.Idle
        elif action == RSNAction.turnOff:
            global TIMER_ON, TIMER_OFF
            # TODO: do something to shut-down
            TIMER_OFF.set()
            TIMER_ON.clear()
            return RSNSM.Off
        else:
            # for other illegal action
            assert 0, "Idle: invalid action: %s" % str(input)


class State_Ready(State):
    def run(self):
        LOGGER.info("Ready")

    def __str__(self): 
        return "State_Ready"
    
    def next(self, input):
        action = map(RSNAction.RSNAction, [input["action"]])[0]
        if action == RSNAction.recvLocReq:
            # TODO: lookup the queried bus location and
            # TODO: response to user directly
            global BUS_TABLE, LOC_REQ_NO
            LOGGER.info("received location request: %s" % input)
            
            # fetch the nearest bus available
            # TODO: this function should be polished
            nearest_bus = None;
            nearest_loc = None;
            nearest_dist = -1;
            for key in BUS_TABLE:
                bus = BUS_TABLE[key]
                if (int(bus["last_update"]) >= int(LOC_REQ_NO) - 1) and (int(bus["last_update"]) <= int(LOC_REQ_NO)):
                    distance = (int(input["original"]["location"][0]) - int(bus["location"][0])) ** 2 + (int(input["original"]["location"][1]) - int(bus["location"][1])) ** 2
                    if nearest_dist < 0 or distance < nearest_dist:
                        nearest_dist = distance
                        nearest_bus = bus
                        nearest_loc = bus["location"]
            
            response_message = {
                                "SM" : "USER_SM",
                                "action" : "recvRes",
                                "location" : nearest_loc, # TODO: location should be fetched from table
                                "busId" : nearest_bus,
                                "original" : input["original"]
                               }

            MessagePasser.directSend(input["original"]["userIP"], input["original"]["userPort"], response_message)
            
            return RSNSM.Ready
        elif action == RSNAction.askBusLoc:
            # periodically ask each buses' location
            # TODO: triggered by host timer
            global GROUP_MEMBER, RSN_ID, ROUTE_NO, LOCAL_ADDR, LOC_REQ_NO
            LOGGER.info("asking each bus' location %s" % BUS_TABLE.keys())
            LOC_REQ_NO = LOC_REQ_NO + 1             # maybe overflow!!!
            
            req_loc_message = {
                               "SM" : "DRIVER_SM",
                               "action" : "recvLocReq",
                               "requestNo" : LOC_REQ_NO,
                               "rsnId" : RSN_ID,
                               "route" : ROUTE_NO,
                               "rsnIP" : LOCAL_ADDR.ip,
                               "rsnPort" : LOCAL_ADDR.port
                               }
            
            #MessagePasser.multicast(GROUP_MEMBER, req_loc_message)
            # TODO: replace the code below with a multicast version

            for member in BUS_TABLE:
                MessagePasser.directSend(BUS_TABLE[member]["addr"].ip, BUS_TABLE[member]["addr"].port, req_loc_message)
 
            return RSNSM.Ready
        elif action == RSNAction.recvDriverLoc:
            # TODO: update local cache
            global BUS_TABLE, ROUTE_NO

            if input["route"] == ROUTE_NO \
                and input["busId"] in BUS_TABLE \
                and input["requestNo"] > BUS_TABLE[input["busId"]]["last_update"]:
                
                BUS_TABLE[input["busId"]] = {
                                              "direction" : input["direction"],
                                              "location" : input["location"],
                                              "addr" : Addr(input["busIP"], input["busPort"]),
                                              "last_update" : input["requestNo"]    # TODO: use local time stamp
                                              }
                print BUS_TABLE
            
            return RSNSM.Ready
        elif action == RSNAction.recvBusChange:
            # TODO: add or remove a bus from current group
            LOGGER.info("Receive bus change request: %s" % input)
            global GROUP_MEMBER, BUS_TABLE, ROUTE_NO, RSN_ID, LOCAL_ADDR
            
            if input["route"] == ROUTE_NO:
                if input["type"] == "add":
                    #if not input["busId"] in BUS_TABLE:
                        #GROUP_MEMBER.append(input["busId"])
                        BUS_TABLE[input["busId"]] = {
                                                      "direction" : input["direction"],
                                                      "location" : input["location"],
                                                      "addr" : Addr(input["busIP"], input["busPort"]),
                                                      "last_update" : 0 # TODO: use local time stamp
                                                      }
                        # send an ACK to driver
                        rsn_ack = {
                                   "SM" : "DRIVER_SM",
                                   "action" : "recvRSNAck",
                                   "route" : ROUTE_NO,
                                   "rsnId" : RSN_ID,
                                   "rsnIP" : LOCAL_ADDR.ip,
                                   "rsnPort" : LOCAL_ADDR.port
                                   }
                        MessagePasser.directSend(input["busIP"], input["busPort"], rsn_ack)
                elif input["type"] == "remove":
                    if input["busId"] in BUS_TABLE:
                        #GROUP_MEMBER.remove(input["busId"])
                        BUS_TABLE.pop(input["busId"])
            return RSNSM.Ready
        
        elif action == RSNAction.recvGSNHB:
            LOGGER.info("Receive GSN heart beat: %s" % input["HBNo"])
            
            global BUS_TABLE, RSN_ID, ROUTE_NO, LOCAL_ADDR, GSN_ADDR
            # send current route table to GSN
            HB_res_message = {
                              "SM" : "GSN_SM",
                              "action" : "recvHBRes",
                              "HBNo" : input["HBNo"],
                              "rsnId" : RSN_ID,
                              "route" : ROUTE_NO,
                              "rsnIP" : LOCAL_ADDR.ip,
                              "rsnPort" : LOCAL_ADDR.port,
                              "busTable" : BUS_TABLE
                              }
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, HB_res_message)
            return  RSNSM.Ready
        elif action == RSNAction.recvRSNResign:
            LOGGER.info("Receive GSN resign")
            TIMER_OFF.set()
            TIMER_ON.clear()
            return RSNSM.Idle
        elif action == RSNAction.turnOff:
            # TODO: do something to shut-down
            TIMER_OFF.set()
            TIMER_ON.clear()
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
    global RSN_SM, TIMER_ON, TIMER_OFF, TIMER_THREAD
    RSN_SM = RSNSM()
    
    # Timer variable
    TIMER_ON = threading.Event()
    TIMER_OFF = threading.Event()

    TIMER_THREAD = threading.Thread(target=timerThread, args=(TIMER_ON, TIMER_OFF))
    TIMER_THREAD.daemon = True

    TIMER_ON.clear()
    TIMER_OFF.set()
    TIMER_THREAD.start()
    #time.sleep(10)




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
