#!/usr/bin/python   

'''
Created on Apr 5, 2014

@author: Terry Li
'''
import os
import json
from Tkinter import *  
import threading
import time
import socket
import collections
import SocketServer
import pickle
import glob


import sys
sys.path += ['../']

import comm.TCPComm as TCPComm
from time import sleep

CONF = {}

MASTER_IP = '127.0.0.1'
MASTER_PORT = 60000
#import google_map


NODES = None
LINKS = None
DIC = None
BUSCNT = None
ROUTTABLE = None
ROUTNODES = None
USERNODES = []
USERROUTE = ""
USERSTOP = 0
ISINIT = False
AUTO_RUN_SCRIPT_FILES = {}
LOGS_FILES = {}

MSG_QUEUE = collections.deque()

# tcp server for receiving
TCP_SERVER = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = pickle.loads(self.request.recv(4096))
        message = data["data"]
        MSG_QUEUE.append(message)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# Initialize tcp server for receiving
def runServer(ip, port):
    
    global TCP_SERVER
        
    TCP_SERVER = ThreadedTCPServer((ip, port), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=TCP_SERVER.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

'''
class Application(Frame):
    
    def setupSim(self):
        global CONF
        file = open("../feedFile.txt", "r")
        for line in file:
            # skip blank lines
            if not line.strip():
                continue

            # ignore comment
            if line.startswith("#"):
                continue
        
            # print line
            line = line.rstrip()
            if line.startswith("CONF"):
                tokens = line.split(' ')
                CONF[tokens[1]] = {"IP" : tokens[2], "Port" : tokens[3]}
                
        file.close()
        
        for player in CONF:
            addr = CONF[player]
            os.system("python ../simulation/simulator.py " + addr["IP"] + " " + addr["Port"] + " " + MASTER_IP + " " + str(MASTER_PORT) + " &")

    
    def startSim(self):
        file = open("../feedFile.txt", "r")
        for line in file:
            # skip blank lines
            if not line.strip():
                continue

            # ignore comment
            if line.startswith("#"):
                continue
        
            # print line
            if line.startswith("CONF") == False:
                tokens = line.split(' ', 1)
                addr = CONF[tokens[0]]
                message = eval(tokens[1])
                #if (message["action"] == "initialize"):
                #    self.writeJsonFile(message["localName"], message["role"], "71A")
                ip = addr["IP"]
                port = int(addr["Port"])
                TCPComm.send(ip, port, message)
           
    def createWidgets(self):
        
        Label(self, text="").grid(row = 0)
        
        self.confBtn = Button(self)
        self.confBtn["text"] = "setup sim"
        self.confBtn["command"] = self.setupSim 
        self.confBtn.grid(row = 7, column = 0)   
        
        self.simBtn = Button(self)
        self.simBtn["text"] = "simulate"
        self.simBtn["command"] = self.startSim 
        self.simBtn.grid(row = 7, column = 1)   
         
  
    def __init__(self, master=None):   
        Frame.__init__(self, master)   
        self.pack()   
        self.createWidgets()   
''' 

def getNodeByName(name):
    for elm in NODES:
        if elm["name"] == name:
            return elm
        
    return None
    
def readRoutTable():
    global ROUTTABLE
    json_data = open('../visualization/coordinates.json')
    ROUTTABLE = json.load(json_data)

def getRoutes():
    global ROUTTABLE
    return ROUTTABLE.keys()

def updateNodePos(name, busLine, idx):
    node = getNodeByName(name)
    if node != None:
        node["x"] = ROUTTABLE[busLine][idx]["x"]
        node["y"] = ROUTTABLE[busLine][idx]["y"]


def getIdxByName(name):
    for i in range(len(NODES)):
        if NODES[i]["name"] == name:
            return NODES[i]["index"]
        
    return 0


def parseDriverMsg(command):
    global NODES, LINKS, DIC, USERNODES
    NODES = []
    LINKS = []
    DIC = {}
    DIC["nodes"] = NODES
    DIC["links"] = LINKS
    
    dic = {}
    dic["index"] = 0
    dic["name"] = "GSN_1"
    dic["type"] = "GSN"
    dic["fixed"] = "true"
    dic["x"] = 420
    dic["y"] = 390

    NODES.append(dic)
    
    rsn_busId = command["busId"]
    bus_table = command["BUS_TABLE"]
    route = command["route"]
    
    if route == USERROUTE:
        for item in bus_table.items():
            if item[1]["location"] == USERSTOP:
                USERNODES = []
                break
        
    
    if USERNODES != None and len(USERNODES) > 0:
        dic = USERNODES[0]
        dic["index"] = len(NODES)
        NODES.append(dic)
    
        link_dic = {}
        link_dic["index"] = len(LINKS)
        link_dic["source"] = 0
        link_dic["target"] = len(NODES) - 1
        LINKS.append(link_dic)
    
   
    
    ROUTNODES[route] = []
            
    rsn_data = bus_table.get(rsn_busId)
    dic = {}
    dic["index"] = len(NODES)
    dic["name"] = rsn_busId
    dic["type"] = "RSN"
              
    dic["fixed"] = "true"
    dic["x"] = ROUTTABLE[route][rsn_data["location"]]["x"]
    dic["y"] = ROUTTABLE[route][rsn_data["location"]]["y"]
    ROUTNODES[route].append(dic)
            
    for item in bus_table.items():
        if item[0] != rsn_busId:
            dic = {}
            dic["index"] = len(NODES)
            dic["name"] = item[0]
            dic["type"] = "DRIVER" 
            dic["fixed"] = "true"
            dic["x"] = ROUTTABLE[route][item[1]["location"]]["x"]
            dic["y"] = ROUTTABLE[route][item[1]["location"]]["y"]
            ROUTNODES[route].append(dic)
                
            
            
    for busLine in ROUTNODES.items():
        busList = busLine[1]
        dic = busList[0]
        dic["index"] = len(NODES)
        NODES.append(dic)
                
        link_dic = {}
        link_dic["index"] = len(LINKS)
        link_dic["source"] = 0
        link_dic["target"] = len(NODES) - 1
        LINKS.append(link_dic)
                
        idx = 0
        for dic in busList:
            if idx != 0:
                dic["index"] = len(NODES)
                NODES.append(dic)
                        
                link_dic = {}
                link_dic["index"] = len(LINKS)
                link_dic["source"] = getIdxByName(busList[0]["name"])
                
                link_dic["target"] = len(NODES) - 1
                LINKS.append(link_dic)
            idx = idx + 1
                
                    
    outfile = open("../visualConsole/static/graph.json", "w")
    json.dump(DIC, outfile)
    outfile.close()
            
            
    locationFile = open("../visualConsole/static/locList.txt", "w")
    for elm in NODES:
        if elm["type"] == "USER" or elm["type"] == "GSN":
            locationFile.write(elm["type"] + ": " + elm["name"] + " " + str(elm["x"]) + " " + str(elm["y"]) + "\n\n")
        elif elm["type"] == "RSN":
            locationFile.write(elm["type"] + ": " + elm["name"] + " " + str(elm["x"]) + " " + str(elm["y"]) + "\n")
        else:
            locationFile.write("    " + elm["type"] + ": " + elm["name"] + " " + str(elm["x"]) + " " + str(elm["y"]) + "\n")
    locationFile.close()


def parseUserMsg(command):
    global USERNODES, USERROUTE, USERSTOP
    # update the user location
    USERNODES = []
    node = {}
    node["index"] = 1
    node["name"] = command["userId"]
    node["type"] = "USER"
    
    route = command["query"]["route"]
    USERROUTE = route
    
    stationIdx = command["query"]["location"]
    USERSTOP = stationIdx
    
    node["fixed"] = "true"
    node["x"] = ROUTTABLE[route][stationIdx]["x"]
    node["y"] = ROUTTABLE[route][stationIdx]["y"]
    
    USERNODES.append(node)
    
    # report the user query result
    locationFile = open("../visualConsole/static/queryResult.txt", "a")
    
    userLoc = str(command["query"]["location"])
    userRoute = str(command["query"]["route"])
    busId = str(command["response"]["busId"])
    busLoc = str(command["response"]["location"])
    if busId == None:
        busId = "None"
        busLoc = "None"
    
    locationFile.write("<tr><td>" + command["userId"] + "</td><td>" + userLoc + "</td><td>" + userRoute + "</td><td>" + busId + "</td><td>" + busLoc + "</td><td>" + str(int(command["arriveTime"]) * 1) + "</td></tr>\n")
  
    locationFile.close()
    
    
def writeJsonFile():
    global ROUTNODES
    ROUTNODES = {}
        
    while True:
        if MSG_QUEUE:
            # get node from message
            command = MSG_QUEUE.popleft()
            if command["SM"] == "RSN_SM":
                parseDriverMsg(command)
            else:
                # message from user
                parseUserMsg(command)
                
            #time.sleep(5)


def initialize(masterIp, masterPort):
    global ISINIT, MASTER_IP, MASTER_PORT, AUTO_RUN_SCRIPT_FILES
    ISINIT = True
    MASTER_IP = masterIp
    MASTER_PORT = masterPort
    
    file_paths = glob.glob("../auto_run_scripts/*.txt")
    
    for path in file_paths:
        AUTO_RUN_SCRIPT_FILES[os.path.basename(path)] = path
    
    clearFiles()
    
    readRoutTable()
    runServer(MASTER_IP, MASTER_PORT)
    thread = threading.Thread(target=writeJsonFile, args = ())
    thread.start()
    

def isInitialized():
    return ISINIT


def launchSimulator(simulatorName, role, ip, port, message):
    global CONF
    CONF[simulatorName] = {"role": role, "IP" : ip, "Port" : port}
    
    # launch simulator
    os.system("python ../simulation/simulator.py " + ip + " " + str(port) + " " + MASTER_IP + " " + str(MASTER_PORT) + " " + simulatorName + " &")
    
    sleep(2)
    # send initialize command
    TCPComm.send(ip, port, message)

def getScripts():
    global AUTO_RUN_SCRIPT_FILES
    return AUTO_RUN_SCRIPT_FILES.keys()

def getLogs():
    global LOGS_FILES
    LOGS_FILES = {}
    file_paths = glob.glob("../visualConsole/static/logs/*.log")

    for path in file_paths:
        LOGS_FILES[os.path.basename(path)] = path

    return LOGS_FILES.keys()

def clearLogs():
    global LOGS_FILES
    for filename in LOGS_FILES:
        os.remove(LOGS_FILES[filename])

def getSimulatorNames():
    global CONF
    
    gsn_list = []
    driver_list = []
    user_list = []
    for name in CONF:
        if CONF[name]["role"] == "GSN":
            gsn_list.append(name)
        elif CONF[name]["role"] == "DRIVER":
            driver_list.append(name)
        elif CONF[name]["role"] == "USER":
            user_list.append(name)
    return {"GSN":gsn_list, "DRIVER":driver_list, "USER":user_list}
    

def sendCmd(simulatorName, message):
    if CONF.has_key(simulatorName) == False:
        return
    
    addr = CONF[simulatorName]
    ip = addr["IP"]
    port = int(addr["Port"])

    if message["action"] == "exit":
        CONF.pop(simulatorName)
        if len(CONF) == 0 or len(CONF) == 1:
            clearFiles()

    TCPComm.send(ip, port, message)


def clearFiles():
    locationFile = open("../visualConsole/static/queryResult.txt", "w")
    locationFile.close()
    
    outfile = open("../visualConsole/static/graph.json", "w")
    outfile.close()
            
            
    locationFile = open("../visualConsole/static/locList.txt", "w")
    locationFile.close()

def terminate():
    message = {}
    message["action"] = "exit"
    
    for simulatorName in CONF.keys():
        sendCmd(simulatorName, message)
        #CONF.pop(simulatorName)
    
    MSG_QUEUE.clear()
    clearFiles()

    
def auto_run(filename):
    global CONF, AUTO_RUN_SCRIPT_FILES

    path = AUTO_RUN_SCRIPT_FILES[filename]
    file = open(path, "r")
    
    for line in file:
        # skip blank lines
        if not line.strip():
            continue

        # ignore comment
        if line.startswith("#"):
            continue
        
        # print line
        line = line.rstrip()
        if line.startswith("CONF"):
            tokens = line.split(' ')
            CONF[tokens[1]] = {"role" : tokens[2], "IP" : tokens[3], "Port" : tokens[4]}
                
    file.close()
    
    print "LAUNCHING ALL PROCESSES"
    for player in CONF:
        addr = CONF[player]
        os.system("python ../simulation/simulator.py " + addr["IP"] + " " + addr["Port"] + " " + MASTER_IP + " " + str(MASTER_PORT) + " " + player + " &")

    sleep(2)
    
    # send orders
    print "SENDING COMMANDS"
    file = open(path, "r")
    #file = open("../auto_run_scripts/all_routes.txt", "r")
    for line in file:
        # skip blank lines
        if not line.strip():
            continue

        # ignore comment
        if line.startswith("#"):
            continue
        
        # print line
        if line.startswith("CONF") == False:
            tokens = line.split(' ', 1)
            addr = CONF[tokens[0]]
            message = eval(tokens[1])
            #if (message["action"] == "initialize"):
            #    self.writeJsonFile(message["localName"], message["role"], "71A")
            ip = addr["IP"]
            port = int(addr["Port"])
            TCPComm.send(ip, port, message)


def djangoMain():
    initialize(MASTER_IP, MASTER_PORT)    
    # start processes
    auto_run("fault_demo.txt")
    

def main():
    djangoMain()
    '''
    readRoutTable()
    global MSG_QUEUE, MASTER_IP, MASTER_PORT

    runServer(MASTER_IP, MASTER_PORT)
    thread = threading.Thread(target=writeJsonFile, args = ())
    thread.start()
    win = Tk()   
    win.title("Master")
    win.geometry("800x400")
    app = Application(master=win)   
    app.mainloop()   
    #root.destroy()  
    '''
    
if __name__ == '__main__':
    # main()
    path = glob.glob("../auto_run_scripts/*.txt")
    print os.path.basename(path[0])
    main()
