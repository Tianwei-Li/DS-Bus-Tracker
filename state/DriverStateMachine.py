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
import threading

from time import sleep
from threading import Timer
import thread

logging.basicConfig()
LOGGER = logging.getLogger("DriverStateMachine")
LOGGER.setLevel(logging.DEBUG)

DRIVER_SM = None

ROUTE_NO = -1
DIRECTION = None
BUS_ID = 0
LOCATION = 1    # should be updated by some other module

LOCAL_ADDR = None
GSN_ADDR = None
RSN_ADDR = None

WATCHDOG = None

RESEND_ELECT_NUM = 0


# Watchdog class for timeout detection
class Watchdog(object):
    
    def __init__(self, time=15.0):
        ''' Class constructor. The "time" argument has the units of seconds. '''
        self._time = time
        return
        
    def startWatchdog(self):
        ''' Starts the watchdog timer. '''
        self._timer = Timer(self._time, self._watchdogEvent)
        self._timer.daemon = True
        self._timer.start()
        return
        
    def petWatchdog(self):
        ''' Reset watchdog timer. '''
        self.stopWatchdog()
        self.startWatchdog()
        return
            
        
    def _watchdogEvent(self):
        '''
        This internal method gets called when the timer triggers. A keyboard 
        interrupt is generated on the main thread. The watchdog timer is stopped 
        when a previous event is tripped.
        '''
        # timeout if don't receive askBusLoc from RSN
        LOGGER.info("timeout")
        RSN_timeout__message = {
                                 "SM" : "DRIVER_SM",
                                 "action" : "timeout",
                                 }
        offerMsg(RSN_timeout__message)
            
        #self.stopWatchdog()
        #thread.interrupt_main()
        return

    def stopWatchdog(self):
        ''' Stops the watchdog timer. '''
        self._timer.cancel()
        

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
            global LOCAL_ADDR, RSN_ADDR, ROUTE_NO, DIRECTION, BUS_ID, LOCATION, WATCHDOG
            
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
                           "busIP" : LOCAL_ADDR.ip,
                           "busPort" : LOCAL_ADDR.port
                           }
            # TODO: should use real gsn 
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, add_message)
            
            # start the watchdog
            WATCHDOG.startWatchdog()
            
            return DriverSM.Init_Waiting
        elif action == DriverAction.timeout:
            # TODO: re-ping
            return DriverSM.Idle
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            RESEND_ELECT_NUM = 0
            WATCHDOG.stopWatchdog()

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
            
            # pet the watch dog
            WATCHDOG.petWatchdog()

            return DriverSM.Ready
        elif action == DriverAction.timeout:
            # not receive the reponse from RSN for 15 secs
            global RESEND_ELECT_NUM
            if RESEND_ELECT_NUM >= 3:
                LOGGER.info("RESEND_ELECT_NUM reaches the limit, reboot now.")
                RESEND_ELECT_NUM = 0
                # restart
                global LOCAL_ADDR, RSN_ADDR, ROUTE_NO, DIRECTION, BUS_ID, LOCATION

                add_message = {
                               "SM" : "GSN_SM",
                               "action" : "recvBusReq",
                               "type" : "add",
                               "route" : ROUTE_NO,
                               "direction" : LOCATION,
                               "busId" : BUS_ID,
                               "location" : LOCATION, 
                               "busIP" : LOCAL_ADDR.ip,
                               "busPort" : LOCAL_ADDR.port
                               }
                # TODO: should use real gsn 
                MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, add_message)
                
                # pet the watch dog
                WATCHDOG.petWatchdog()
                
                return DriverSM.Init_Waiting
            else:
                # re-send re-elect msg
                LOGGER.info("send re-elect request to GSN, RESEND_ELECT_NUM: %s" % str(RESEND_ELECT_NUM))
                RESEND_ELECT_NUM = RESEND_ELECT_NUM + 1
                RSN_elect_message = {
                                     "SM" : "GSN_SM",
                                     "action" : "recvElecReq",
                                     "busId" : BUS_ID,
                                     "route" : ROUTE_NO,
                                     "direction" : DIRECTION,
                                     "location" : LOCATION,
                                     "busIP" : LOCAL_ADDR.ip,
                                     "busPort" : LOCAL_ADDR.port
                                     }
                MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, RSN_elect_message)
                
                # pet the watch dog
                WATCHDOG.petWatchdog()
                
                return DriverSM.Init_Waiting
            
            return DriverSM.Init_Waiting
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            RESEND_ELECT_NUM = 0
            WATCHDOG.stopWatchdog()
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
            global ROUTE_NO, DIRECTION, LOCATION, RSN_ADDR, LOCAL_ADDR, BUS_ID, WATCHDOG
            LOGGER.info("received RSN location request: %s" % input)
            
            # pet the watch dog
            WATCHDOG.petWatchdog()
            
            loc_message = {
                           "SM" : "RSN_SM",
                           "action" : "recvDriverLoc",
                           "requestNo" : input["requestNo"],
                           "route" : ROUTE_NO,
                           "direction" : LOCATION,
                           "busId" : BUS_ID,
                           "location" : LOCATION, 
                           "busIP" : LOCAL_ADDR.ip,
                           "busPort" : LOCAL_ADDR.port
                           }
            # TODO: TEST ONLY; rsn should be modified
            MessagePasser.directSend(RSN_ADDR.ip, RSN_ADDR.port, loc_message)
            
            return DriverSM.Ready
        elif action == DriverAction.timeout:
            # don't hear from RSN for 15 secs
            # send re-elect message to GSN
            global ROUTE_NO, DIRECTION, LOCATION, GSN_ADDR, LOCAL_ADDR, BUS_ID, WATCHDOG
            LOGGER.info("send re-elect request to GSN")
            RSN_elect_message = {
                                 "SM" : "GSN_SM",
                                 "action" : "recvElecReq",
                                 "busId" : BUS_ID,
                                 "route" : ROUTE_NO,
                                 "direction" : DIRECTION,
                                 "location" : LOCATION,
                                 "busIP" : LOCAL_ADDR.ip,
                                 "busPort" : LOCAL_ADDR.port
                                 }
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, RSN_elect_message)
            WATCHDOG.petWatchdog()
            return DriverSM.Hold
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            RESEND_ELECT_NUM = 0
            WATCHDOG.StopWatchdog()
            return DriverSM.Off
        else:
            # for other illegal action
            assert 0, "Ready: invalid action: %s" % str(input)


class State_Hold(State):
    def run(self):
        LOGGER.info("Hold")

    def __str__(self): 
        return "State_Hold"
    
    def next(self, input):
        action = map(DriverAction.DriverAction, [input["action"]])[0]
        if action == DriverAction.recvLocReq:
            # TODO: response the current location
            # check if the rsn is my RSN, route matched?
            global ROUTE_NO, DIRECTION, LOCATION, RSN_ADDR, LOCAL_ADDR, BUS_ID, WATCHDOG
            LOGGER.info("received RSN location request: %s" % input)
            
            # pet the watch dog
            WATCHDOG.petWatchdog()
            
            # check if the RSN has changed
            if RSN_ADDR.ip != input["rsnIP"] or RSN_ADDR.port != input["rsnPort"]:
                LOGGER.info("RSN has changed")
                RSN_ADDR = Addr(input["rsnIP"], input["rsnPort"])
            
            loc_message = {
                           "SM" : "RSN_SM",
                           "action" : "recvDriverLoc",
                           "requestNo" : input["requestNo"],
                           "route" : ROUTE_NO,
                           "direction" : LOCATION,
                           "busId" : BUS_ID,
                           "location" : LOCATION, 
                           "busIP" : LOCAL_ADDR.ip,
                           "busPort" : LOCAL_ADDR.port
                           }
            # TODO: TEST ONLY; rsn should be modified
            MessagePasser.directSend(RSN_ADDR.ip, RSN_ADDR.port, loc_message)
            
            return DriverSM.Ready
        
        elif action == DriverAction.restart:
            # restart
            global LOCAL_ADDR, RSN_ADDR, ROUTE_NO, DIRECTION, BUS_ID, LOCATION, RESEND_ELECT_NUM

            LOGGER.info("Receive restart message from GSN. Restart now.")
                
                
            # TODO: ping RSN to add into the group
            add_message = {
                           "SM" : "GSN_SM",
                           "action" : "recvBusReq",
                           "type" : "add",
                           "route" : ROUTE_NO,
                           "direction" : LOCATION,
                           "busId" : BUS_ID,
                           "location" : LOCATION, 
                           "busIP" : LOCAL_ADDR.ip,
                           "busPort" : LOCAL_ADDR.port
                           }
            # TODO: should use real gsn 
            MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, add_message)

            RESEND_ELECT_NUM = 0
            
            # pet the watch dog
            WATCHDOG.petWatchdog()
            
            return DriverSM.Init_Waiting
        elif action == DriverAction.timeout:
            # if reaches the limit of re-elect, reboot
            global RESEND_ELECT_NUM
            if RESEND_ELECT_NUM >= 3:
                LOGGER.info("RESEND_ELECT_NUM reaches the limit, reboot now.")
                RESEND_ELECT_NUM = 0
                # restart
                global LOCAL_ADDR, RSN_ADDR, ROUTE_NO, DIRECTION, BUS_ID, LOCATION

                add_message = {
                               "SM" : "GSN_SM",
                               "action" : "recvBusReq",
                               "type" : "add",
                               "route" : ROUTE_NO,
                               "direction" : LOCATION,
                               "busId" : BUS_ID,
                               "location" : LOCATION, 
                               "busIP" : LOCAL_ADDR.ip,
                               "busPort" : LOCAL_ADDR.port
                               }
                # TODO: should use real gsn 
                MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, add_message)
                
                # pet the watch dog
                WATCHDOG.petWatchdog()
                
                return DriverSM.Init_Waiting
            else:
                # re-send re-elect msg
                LOGGER.info("send re-elect request to GSN, RESEND_ELECT_NUM: %s" % str(RESEND_ELECT_NUM))
                RESEND_ELECT_NUM = RESEND_ELECT_NUM + 1
                RSN_elect_message = {
                                     "SM" : "GSN_SM",
                                     "action" : "recvElecReq",
                                     "busId" : BUS_ID,
                                     "route" : ROUTE_NO,
                                     "direction" : DIRECTION,
                                     "location" : LOCATION,
                                     "busIP" : LOCAL_ADDR.ip,
                                     "busPort" : LOCAL_ADDR.port
                                     }
                MessagePasser.directSend(GSN_ADDR.ip, GSN_ADDR.port, RSN_elect_message)
                
                # pet the watch dog
                WATCHDOG.petWatchdog()
                
                return DriverSM.Hold
        elif action == DriverAction.turnOff:
            # TODO: do something to shut-down
            RESEND_ELECT_NUM = 0
            WATCHDOG.stopWatchdog()
            return DriverSM.Off
        else:
            # for other illegal action
            assert 0, "Init_Waiting: invalid action: %s" % str(input)
            
            
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
    global DRIVER_SM, WATCHDOG
    DRIVER_SM = DriverSM()
    WATCHDOG = Watchdog(15)
    

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
DriverSM.Hold = State_Hold()

        
# Test Only
if __name__ == '__main__':
    dog = Watchdog(1)
    dog.startWatchdog()
    while True:
        sleep(3)
        dog.petWatchdog()
        pass
