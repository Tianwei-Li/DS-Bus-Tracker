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
RoutTable = []

class AddrTableElm:
    IP = None
    Port = 0

class RoutTableElm:
    rsnIP = None
    rsnPort = 0
    routName = ""
    AddrTableElem = []

def getRSNByName(routName):
    for elm in RoutTable:
        if routName == elm.routName:
            return elm
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
        
        elif input == GSNAction.recvBusReq:
            # TODO: update route table and forward user request to responding RSN
            LOGGER.info("forward bus request to RSN")
            rsnAddr = getRSNByName(input["route"])
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
        elif input == GSNAction.turnOff:
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