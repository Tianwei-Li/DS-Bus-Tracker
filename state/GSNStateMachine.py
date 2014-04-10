'''
Created on Apr 5, 2014

@author: Qian Mao
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.GSNAction as GSNAction
import comm.MessagePasser as MessagePasser
import util.RouteTableElm as RouteTableElm
from util.Addr import Addr
import util.BusTableElm as BusTableElm

logging.basicConfig()
LOGGER = logging.getLogger("GSNStateMachine")
LOGGER.setLevel(logging.DEBUG)

GSN_SM = None
ROUTE_TABLE = {}

GSN_ID = None
LOCAL_ADDR = None

def getRSNByName(routeName):
    global ROUTE_TABLE
    if routeName in ROUTE_TABLE:
        return ROUTE_TABLE[routeName]
    return None
            

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")
        
    def __str__(self): 
        return "State_Off"

    def next(self, input):
        action = map(GSNAction.GSNAction, [input["action"]])[0]
        if action == GSNAction.turnOn:
            global LOCAL_ADDR, GSN_ID
            # do something about boot-strap
            # Qian: seems we don't need to do anything
            LOCAL_ADDR = Addr(input["localIP"], input["localPort"])
            GSN_ID = input["gsnId"]
            
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
        action = map(GSNAction.GSNAction, [input["action"]])[0]
        if action == GSNAction.recvUserReq:
            # TODO: forward user request to responding RSN
            LOGGER.info("forward user request to RSN")
            rsnAddr = getRSNByName(input["route"])
            request_message = {
                               "SM" : "RSN_SM",
                               "action" : "recvLocReq",
                               "original" : input
                               }
            MessagePasser.directSend(rsnAddr.rsnIP, rsnAddr.rsnPort, request_message)
            
            return GSNSM.Ready
        
        elif action == GSNAction.recvBusReq:
            # TODO: update route table and forward user request to responding RSN
            LOGGER.info("receive bus request")
            rsnAddr = getRSNByName()
            # if there is no RSN, assign the request bus as the RSN
            if rsnAddr == None:
                # Qian: some checks: (1) if there is no rsn but receive a remove req
                LOGGER.info("assign new RSN")
                """
                routeTableElm = RouteTableElm(input["route"], 
                                              Addr(input["driverIp"], input["driverPort"]), 
                                              [])
                routeTableElm.busTable.append(BusTableElm(Addr(input["driverIp"], input["driverPort"])))
                """
                
                ROUTE_TABLE[input["route"]] = None
                assign_message = {
                                  "SM" : "RSN_SM",
                                  "action" : "recvRSNAssign",
                                  "type" : "self", 
                                  "route" : input["route"],
                                  "original" : input,
                                  "groupMember" : [input["busId"]]
                                  }
                
                MessagePasser.directSend(input["driverIp"], input["driverPort"], assign_message)
            else:
                # Qian: GSN will just forward it to rsn
                # may change this design
                request_message = {
                                   "SM" : "RSN_SM",
                                   "action" : "recvBusChange",
                                   "type" : input["type"],    # add or remove
                                   "route" : input["route"],
                                   "busIP" : input["busIP"],
                                   "busPort" : input["busPort"]
                                   }
                MessagePasser.directSend(rsnAddr.rsnIP, rsnAddr.rsnPort, request_message)
            return GSNSM.Ready
        elif action == GSNAction.recvElecReq:
            # receive election rsn request for a bus
            route_no = input["routeNo"]
            elm = getRSNByName(route_no)
            # TODO: select a bus from the table to be the new rsn, below code just selects the first driver
            elm.rsnIP = elm.busTable[0].IP
            elm.rsnPort = elm.busTable[0].Port
            
            LOGGER.info("send message to new rsn")
            assign_message = {
                              "SM" : "RSN_SM",
                              "action" : "recvRSNAssign",
                              "groupMember" : elm.busTable
                              }
            # TODO: TEST ONLY; gsn should be modified
            MessagePasser.directSend(elm.rsnIP, elm.rsnPort, request_message)
            
            return GSNSM.Ready
        elif action == GSNAction.turnOff:
            # TODO: do something to shut-down
            return GSNSM.Off


    
class GSNSM(StateMachine):
    def __init__(self):
        # Initial state
        StateMachine.__init__(self, GSNSM.Off)
        
    def run(self, input):
        self.currentState = self.currentState.next(input)
        self.currentState.run()
        
    def runAll(self, inputs):
        for input in inputs:
            self.run(input)
            
    def state(self):
        return self.currentState
        
def initialize():
    global GSN_SM
    GSN_SM = GSNSM()

def offerMsg(message):
    global GSN_SM
    if message["SM"] == "GSN_SM":
        GSN_SM.run(message)
        
def offerMsgs(messages):
    for message in messages:
        offerMsg(message)

GSNSM.Off = State_Off()
GSNSM.Ready = State_Ready()