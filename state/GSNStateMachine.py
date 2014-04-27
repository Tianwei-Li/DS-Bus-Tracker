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

import threading

logging.basicConfig()
LOGGER = logging.getLogger("GSNStateMachine")
LOGGER.setLevel(logging.DEBUG)

GSN_SM = None
'''
key        value
route     "rsnId" : busId,
          "rsnAddr" : Addr(busIP, busPort)
          "busTable" : 
          "last_update" : timestamp
          "isElect" : True/False
'''
ROUTE_TABLE = {}

GSN_ID = None
LOCAL_ADDR = None

TIMER_ON = None
TIMER_OFF = None
TIMER_THREAD = None

HB_NO = 0

# Timer thread
def timerThread(timerOn, timerOff):
    while timerOn.wait():
        while not timerOff.wait(5):     # every 5 secs
            # send a askBusLoc to RSN_SM
            heartbeat_message = {
                                 "SM" : "GSN_SM",
                                 "action" : "heartBeat"
                                 }
            offerMsg(heartbeat_message)

def getRSNByName(routeName):
    global ROUTE_TABLE
    if routeName in ROUTE_TABLE:
        return ROUTE_TABLE[routeName]
    return None
            

class State_Off(State):
    def run(self):
        LOGGER.info("OFF")
        
    def __repr__(self): 
        return "State_Off"

    def next(self, input):
        action = map(GSNAction.GSNAction, [input["action"]])[0]
        if action == GSNAction.turnOn:
            global LOCAL_ADDR, GSN_ID, TIMER_OFF, TIMER_ON
            # do something about boot-strap
            # Qian: seems we don't need to do anything
            LOCAL_ADDR = Addr(input["localIP"], input["localPort"])
            GSN_ID = input["gsnId"]
            
            # unblock the timer thread
            TIMER_OFF.clear()
            TIMER_ON.set()
            
            return GSNSM.Ready
        else:
            # remain off
            return GSNSM.Off
    
class State_Ready(State):
    def run(self):
        LOGGER.info("Ready")
        
    def __repr__(self): 
        return "State_Ready"

    def next(self, input):
        action = map(GSNAction.GSNAction, [input["action"]])[0]
        if action == GSNAction.recvUserReq:
            # TODO: forward user request to responding RSN
            LOGGER.info("receive user request")
            rsn = getRSNByName(input["route"])
            
            if rsn != None:
                LOGGER.info("forward user request to RSN")
                rsnAddr = rsn["rsnAddr"]
                request_message = {
                                   "SM" : "RSN_SM",
                                   "action" : "recvLocReq",
                                   "original" : input
                                   }
                MessagePasser.directSend(rsnAddr.ip, rsnAddr.port, request_message)
            else:
                LOGGER.info("no rsn running")
                response_message = {
                                    "SM" : "USER_SM",
                                    "action" : "recvRes",
                                    "location" : None, 
                                    "busId" : None,
                                    "original" : input
                                    }
                MessagePasser.directSend(input["userIP"], input["userPort"], response_message)
            
            return GSNSM.Ready
        
        elif action == GSNAction.heartBeat:
            LOGGER.info("send heart beat to each RSN")
            global HB_NO
            HB_NO = HB_NO + 1
            
            hb_message = {
                          "SM" : "RSN_SM",
                          "action" : "recvGSNHB",
                          "HBNo" : HB_NO
                          }

            for route in ROUTE_TABLE:
                MessagePasser.directSend(ROUTE_TABLE[route]["rsnAddr"].ip, ROUTE_TABLE[route]["rsnAddr"].port, hb_message)
            
            return GSNSM.Ready
        
        elif action == GSNAction.recvHBRes:
            LOGGER.info("receive HB response")
            
            global ROUTE_TABLE, HB_NO
            
            # update ROUTE_TABLE
            if input["route"] in ROUTE_TABLE:
                if input["rsnId"] == ROUTE_TABLE[input["route"]]["rsnId"]:
                    ROUTE_TABLE[input["route"]]["rsnAddr"] = Addr(input["rsnIP"], input["rsnPort"])
                    ROUTE_TABLE[input["route"]]["busTable"] = input["busTable"]
                    ROUTE_TABLE[input["route"]]["last_update"] = input["HBNo"]
                    ROUTE_TABLE[input["route"]]["isElect"] = False
                else:
                    # TODO: the rsnId is not recorded
                    pass
            else:
                # TODO: the route is not recorded.
                pass
            
            return GSNSM.Ready
        elif action == GSNAction.recvBusReq:
            # TODO: update route table and forward user request to responding RSN
            LOGGER.info("receive bus request")
            rsn = getRSNByName(input["route"])
            # if there is no RSN, assign the request bus as the RSN
            if rsn == None:
                # Qian: some checks: (1) if there is no rsn but receive a remove req
                LOGGER.info("assign new RSN")
                """
                routeTableElm = RouteTableElm(input["route"], 
                                              Addr(input["driverIp"], input["driverPort"]), 
                                              [])
                routeTableElm.busTable.append(BusTableElm(Addr(input["driverIp"], input["driverPort"])))
                """
                route_table_entry = {
                                     "rsnId" : input["busId"],
                                     "rsnAddr" : Addr(input["busIP"], input["busPort"]),
                                     "busTable" : None,
                                     "last_update" : HB_NO
                                     }
                
                ROUTE_TABLE[input["route"]] = route_table_entry
                assign_message = {
                                  "SM" : "RSN_SM",
                                  "action" : "recvRSNAssign",
                                  "type" : "self", 
                                  "route" : input["route"],
                                  "original" : input,
                                  "groupMember" : [input["busId"]]
                                  }
                
                MessagePasser.directSend(input["busIP"], input["busPort"], assign_message)
            else:
                # Qian: GSN will just forward it to rsn
                # may change this design
                request_message = {
                                   "SM" : "RSN_SM",
                                   "action" : "recvBusChange",
                                   "type" : input["type"],    # add or remove
                                   "route" : input["route"],
                                   "direction" : input["direction"],
                                   "location" : input["location"],
                                   "busId" : input["busId"],
                                   "busIP" : input["busIP"],
                                   "busPort" : input["busPort"]
                                   }
                MessagePasser.directSend(rsn["rsnAddr"].ip, rsn["rsnAddr"].port, request_message)
            return GSNSM.Ready
        elif action == GSNAction.recvElecReq:
            # receive election rsn request for a bus
            LOGGER.info("receive election request")
            global HB_NO
            
            rsn = getRSNByName(input["route"])
            
            # check if the rsn is live by checking the time stamp
            if rsn["last_update"] + 1 >= HB_NO:
                # means the RSN is alive, tell the driver to wait or reboot
                if rsn["isElect"] == True:
                    LOGGER.info("new RSN has been elected, ignore the elect request")
                else:
                    LOGGER.info("RSN is alive, ask the driver to reboot")
                    restart_message = {
                                       "SM" : "DRIVER_SM",
                                       "action" : "restart"
                                       }
                    MessagePasser.directSend(input["busIP"], input["busPort"], restart_message)
            else:
                # the RSN is dead, elect a new one, select the bus who sends the request, #with the longest potential running time
                
                
                bus_table = rsn["busTable"]
                '''
                rsn_candidate = None
                min_dist = -1
                min_bus_id = -1
                
                for bus in bus_table:
                    dist = int(bus_table[bus]["location"])
                    if min_dist < 0 or dist < min_dist:
                        min_dist = dist
                        rsn_candidate = bus_table[bus]
                        min_bus_id = bus
                '''
                LOGGER.info("RSN is dead, select a new RSN [%s] for route [%s]" % (input["busId"], input["route"]))
                

                
                # explicitly send a message to shut down the previous RSN
                resign_message = {
                                  "SM" : "RSN_SM",
                                  "action" : "recvRSNResign"
                                  }
                MessagePasser.directSend(rsn["rsnAddr"].ip, rsn["rsnAddr"].port, resign_message)

                
                # assign a new RSN
                assign_message = {
                                  "SM" : "RSN_SM",
                                  "action" : "recvRSNAssign",
                                  "type" : "normal", 
                                  "route" : input["route"],
                                  "original" : None,
                                  "busTable" : bus_table
                                  }
                
                ROUTE_TABLE[input["route"]] = {
                                               "rsnId" : input["busId"],
                                               "rsnAddr" : Addr(input["busIP"], input["busPort"]),
                                               "busTable" : bus_table,
                                               "last_update" : HB_NO,
                                               "isElect" : True,
                                               }
                
                MessagePasser.directSend(input["busIP"], input["busPort"], assign_message)
                
            
            # TODO: select a bus from the table to be the new rsn, below code just selects the first driver
            '''
            elm.rsnIP = elm.busTable[0]["rsnAddr"].ip
            elm.rsnPort = elm.busTable[0]["rsnAddr"].port
            
            LOGGER.info("send message to new rsn")
            assign_message = {
                              "SM" : "RSN_SM",
                              "action" : "recvRSNAssign",
                              "groupMember" : elm.busTable
                              }
            # TODO: TEST ONLY; gsn should be modified
            MessagePasser.directSend(elm.rsnIP, elm.rsnPort, request_message)
            '''
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
        return str(self.currentState)
        
def initialize():
    global GSN_SM, TIMER_OFF, TIMER_ON
    GSN_SM = GSNSM()
    
    # Timer variable
    TIMER_ON = threading.Event()
    TIMER_OFF = threading.Event()

    TIMER_THREAD = threading.Thread(target=timerThread, args=(TIMER_ON, TIMER_OFF))
    TIMER_THREAD.daemon = True

    TIMER_ON.clear()
    TIMER_OFF.set()
    TIMER_THREAD.start()

def offerMsg(message):
    global GSN_SM
    if message["SM"] == "GSN_SM":
        GSN_SM.run(message)
        
def offerMsgs(messages):
    for message in messages:
        offerMsg(message)
        
def state():
    global GSN_SM
    return GSN_SM.currentState

GSNSM.Off = State_Off()
GSNSM.Ready = State_Ready()