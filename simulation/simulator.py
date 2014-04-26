'''
Created on Apr 24, 2014

@author: Qian Mao
'''
import sys
sys.path += ['../']

import host.host as host
import logging
import socket
import collections
import SocketServer
import pickle
import threading
import os
import util.Location as Location
from time import sleep
import comm.TCPComm as TCPComm
#import json


logging.basicConfig()
LOGGER = logging.getLogger("Simulator")
LOGGER.setLevel(logging.DEBUG)

TCP_IP = '127.0.0.1'
TCP_PORT = 9999

MASTER_IP = '127.0.0.1'
MASTER_PORT = 60000


MSG_QUEUE = collections.deque()

# tcp server for receiving
TCP_SERVER = None

TIMER_ON1 = None
TIMER_OFF1 = None
TIMER_THREAD1 = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = pickle.loads(self.request.recv(1024))
        message = data["data"]
        MSG_QUEUE.append(message)
        LOGGER.info("Receive message from %s : %s", self.request.getpeername(), data)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# Initialize tcp server for receiving
def runServer(ip, port):
    LOGGER.info("Lisenting on (%s, %d)", ip, port)
    
    global TCP_SERVER
        
    TCP_SERVER = ThreadedTCPServer((ip, port), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=TCP_SERVER.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
        
def reporterThread():
    global MASTER_IP, MASTER_PORT
    
    while True:
        state = host.state()
        if state != None:
            LOGGER.info("report state: %s" % state)
            TCPComm.send(MASTER_IP, MASTER_PORT, state)
        sleep(5)

def updateLocThread():
    while True:
        Location.moveOneStop()
        LOGGER.info("Update Location")
        sleep(10)       # take 10 seconds to move to next stop


# should be called by master
if __name__ == '__main__':
    global MSG_QUEUE, TCP_IP, TCP_PORT    

    LOGGER.info("Simulator starts! Hello from simulator!")

    TCP_IP = sys.argv[1]
    TCP_PORT = int(sys.argv[2])
    
    runServer(TCP_IP, TCP_PORT)
    
    # initialize reporter thread
    reporterThread = threading.Thread(target=reporterThread, args = ())
    reporterThread.daemon = True
    reporterThread.start()
    
    # initialize updateLocThread
    updateLocThread = threading.Thread(target=updateLocThread, args = ())
    updateLocThread.daemon = True
    updateLocThread.start()
    
    while True:
        if MSG_QUEUE:
            command = MSG_QUEUE.popleft()
            if command["action"] == "initialize":
                host.initialize(command["localName"], command["role"], command["id"], command["localIP"], command["localPort"])
            if command["action"] == "start":    # start a bus
                host.enqueue({"SM":"DRIVER_SM", "action":"start", "route":command["route"], "direction":command["direction"], "location":command["location"]})
            if command["action"] == "request":  # user send a request
                host.enqueue({"SM":"USER_SM", "action":"request", "route":command["route"], "direction":command["direction"], "destination":command["destination"], "location":command["location"]})
            if command["action"] == "sleep":
                sleep(command["time"])
            if command["action"] == "exit":
                os._exit(0)
        sleep(0.1)
        
