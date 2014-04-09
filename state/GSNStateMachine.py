'''
Created on Apr 5, 2014

@author: Qian Mao
'''

import logging
from state.State import State
from state.StateMachine import StateMachine
import action.GSNAction as GSNAction
import comm.MessagePasser as MessagePasser

logging.basicConfig()
LOGGER = logging.getLogger("GSNStateMachine")
LOGGER.setLevel(logging.DEBUG)

GSN_SM = None
ROUTE_TABLE = {}

class Addr:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

class RoutTableElm:
    def __init__(self, routeName, rsnAddr, busTable):
        self.rsnAddr = rsnAddr
        self.routeName = routeName
        self.busTable = busTable

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
        action = map(GSNAction.GSNAction, [input["action"]])[0]
        if action == GSNAction.recvUserReq:
            # TODO: forward user request to responding RSN
            LOGGER.info("forward user request to RSN")
            rsnAddr = getRSNByName(input["route"])
            request_message = {
                               "SM" : "RSN_SM",
                               "action" : "recvLocReq",
                               "route" : input["route"],
                               "direction" : input["direction"],
                               "destination" : input["destination"],
                               "userIP" : input["userIP"],
                               "userPort" : input["userPort"]
                               }
            MessagePasser.directSend(rsnAddr.rsnIP, rsnAddr.rsnPort, request_message)
            
            return GSNSM.Ready
        
        elif action == GSNAction.recvBusReq:
            # TODO: update route table and forward user request to responding RSN
            LOGGER.info("forward bus request to RSN")
            rsnAddr = getRSNByName()
            # if there is no RSN, assign the request bus as the RSN
            if rsnAddr == None:
                ROUTE_TABLE[input["route"]] = RoutTableElm(input["route"], 
                                                           Addr(input["ip"], input["port"]), 
                                                           [Addr(input["ip"], input["port"])])
                assign_message = {
                              "SM" : "RSN_SM",
                              "action" : "recvRSNAssign",
                              "groupMember" : elm.busTable
                              }
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