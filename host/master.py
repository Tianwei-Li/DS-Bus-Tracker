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

MSG_QUEUE = collections.deque()

# tcp server for receiving
TCP_SERVER = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = pickle.loads(self.request.recv(1024))
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

class Application(Frame):
        
    '''    
    def newUser(self):
        name = self.userName.get()
        ip = self.userIP.get()
        port = self.userPort.get()
        routNo = self.queryRout.get()
        #routNo = "ttt"
        interval = "50"
        #interval = self.timeInter.get()
        print "new user launched!"
        #os.system("python gui_user.py " + ip + " " + port + " " + name + " " + routNo + " " + interval + " &")
        
        self.writeJsonFile(name, "USER", "")
    
    def newGSN(self):   
        name = self.gsnName.get()
        ip = self.gsnIP.get()
        port = self.gsnPort.get()
        print "new GSN launched!"  
        #print name + " " + ip + " " + port
        #os.system("python gui_gsn.py " + ip + " " + port + " " + name + " &")
        
        self.writeJsonFile(name, "gsn", "")
        
    def newDriver(self):  
        name = self.driverName.get() 
        ip = self.driverIP.get()
        port = self.driverPort.get()
        routNo = self.routeNo.get()
        #routNo = "61A"
        print "new driver launched!"  
        #os.system("python gui_driver.py " + ip + " " + port + " " + name + " " + routNo + " &")
        
        if BUSCNT.has_key(routNo) == True:
            self.writeJsonFile(name, "DRIVER", routNo)
            BUSCNT[routNo] += 1
            
        else:
            self.writeJsonFile("RSN-"+routNo, "RSN", routNo)
            BUSCNT[routNo] = 1
            #for idx in range(29):
            #    self.updateJsonFile("RSN-"+routNo, "RSN", routNo, idx)
            #    time.sleep(2)
 
    def createUser(self, col):
        Label(self, text="name:").grid(row = 1, column = col)
        defaultName = StringVar()
        defaultName.set("alice")
        self.userName = Entry(self, textvariable = defaultName)
        self.userName.grid(row = 1, column = col+1)
        
        Label(self, text="IP:").grid(row = 2, column = col)
        defaultIP = StringVar()
        defaultIP.set("127.0.0.1")        
        self.userIP = Entry(self, textvariable = defaultIP)
        self.userIP.grid(row = 2, column = col+1)
        
        Label(self, text="Port:").grid(row = 3, column = col)
        defaultPort = StringVar()
        defaultPort.set("30000")
        self.userPort = Entry(self, textvariable = defaultPort)
        self.userPort.grid(row = 3, column = col+1)  
        
        
        Label(self, text="Route:").grid(row = 4, column = col)
        defaultRoute = StringVar()
        defaultRoute.set("61C")
        self.queryRout = Entry(self, textvariable = defaultRoute)
        self.queryRout.grid(row = 4, column = col+1) 
        
        
        Label(self, text="Query Interval:").grid(row = 5, column = col)
        defaultInterv = StringVar()
        defaultInterv.set("10 s")
        self.timeInter = Entry(self, textvariable = defaultInterv)
        self.timeInter.grid(row = 5, column = col+1) 
        
        self.newUserBtn = Button(self)
        self.newUserBtn["text"] = "launch user"
        self.newUserBtn["command"] = self.newUser 
        self.newUserBtn.grid(row = 6, column = col+1)   
        
    def createGSN(self, col):
        Label(self, text="name:").grid(row = 1, column = col)
        defaultName = StringVar()
        defaultName.set("gsn")
        self.gsnName = Entry(self, textvariable = defaultName)
        self.gsnName.grid(row = 1, column = col+1)
        
        Label(self, text="IP:").grid(row = 2, column = col)
        defaultIP = StringVar()
        defaultIP.set("127.0.0.1")
        self.gsnIP = Entry(self, textvariable = defaultIP)
        self.gsnIP.grid(row = 2, column = col+1)
        
        Label(self, text="Port:").grid(row = 3, column = col)
        defaultPort = StringVar()
        defaultPort.set("40000")
        self.gsnPort = Entry(self, textvariable = defaultPort)
        self.gsnPort.grid(row = 3, column = col+1) 
           
        self.newGSNBtn = Button(self)   
        self.newGSNBtn["text"] = "launch GSN"  
        self.newGSNBtn["command"] =  self.newGSN   
        self.newGSNBtn.grid(row = 6, column = col+1)  
        
    def createDriv(self, col): 
        Label(self, text="name:").grid(row = 1, column = col)
        defaultName = StringVar()
        defaultName.set("driver1")
        self.driverName = Entry(self, textvariable = defaultName)
        self.driverName.grid(row = 1, column = col+1)
        
        Label(self, text="IP:").grid(row = 2, column = col)
        defaultIP = StringVar()
        defaultIP.set("127.0.0.1")
        self.driverIP = Entry(self, textvariable = defaultIP)
        self.driverIP.grid(row = 2, column = col+1) 
        
        Label(self, text="Port:").grid(row = 3, column = col)
        defaultPort = StringVar()  
        defaultPort.set("41000")
        self.driverPort = Entry(self, textvariable = defaultPort)
        self.driverPort.grid(row = 3, column = col+1) 
        
        Label(self, text="Route:").grid(row = 4, column = col)
        defaultRoute = StringVar()  
        defaultRoute.set("61A")
        self.routeNo = Entry(self, textvariable = defaultRoute)
        self.routeNo.grid(row = 4, column = col+1) 
        
        self.newDriBtn = Button(self)   
        self.newDriBtn["text"] = "launch Driver"  
        #self.newGSNBtn["fg"]   = "red"  
        self.newDriBtn["command"] =  self.newDriver   
        self.newDriBtn.grid(row = 6, column = col+1)  
    '''
    
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
        #self.createUser(0)
        #self.createGSN(2)
        #self.createDriv(4)
        
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
 

def getNodeByName(name):
    for elm in NODES:
        if elm["name"] == name:
            return elm
        
    return None
    
def readRoutTable():
    global ROUTTABLE
    json_data = open('../host/coordinates.json')
    ROUTTABLE = json.load(json_data)


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
    
def writeJsonFile():
    global NODES, LINKS, DIC, ROUTNODES
    ROUTNODES = {}
    '''
    dic = {}
    dic["index"] = len(NODES)
    dic["name"] = "qianmao2"
    dic["type"] = "USER"
    NODES.append(dic)
    
    link_dic = {}
    link_dic["index"] = len(LINKS)
    link_dic["source"] = 0
    link_dic["target"] = len(NODES) - 1
    LINKS.append(link_dic)
    '''
        
    while True:
        if MSG_QUEUE:
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
    
            dic = {}
            dic["index"] = len(NODES)
            dic["name"] = "qianmao"
            dic["type"] = "USER" 
            NODES.append(dic)
    
            link_dic = {}
            link_dic["index"] = len(LINKS)
            link_dic["source"] = 0
            link_dic["target"] = len(NODES) - 1
            LINKS.append(link_dic)
            
            
            
            # get node from message
            command = MSG_QUEUE.popleft()
            rsn_busId = command["busId"]
            bus_table = command["BUS_TABLE"]
            route = command["route"]
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
                if elm["type"] != "USER":
                    locationFile.write(elm["name"] + " " + str(elm["x"]) + " " + str(elm["y"]) + "\n")
                else:
                    locationFile.write(elm["name"] + "\n")
            locationFile.close()
            
            time.sleep(5)

'''
def updateJsonFile():
    
    while True:
        if MSG_QUEUE:
            command = MSG_QUEUE.popleft()
            for item in command.items():
                updateNodePos(item[0], "71A", item[1])
            outfile = open("../visualization/graph.json", "w")
            json.dump(DIC, outfile)
            outfile.close()
            
            locationFile = open("../visualization/locList.txt", "w")
            for elm in NODES:
                if elm["type"] == "DRIVER" or elm["type"] == "RSN":
                    locationFile.write(elm["name"] + " " + str(elm["x"]) + " " + str(elm["y"]) + "\n")
            locationFile.close()
            time.sleep(5)
'''

def djangoMain():
    readRoutTable()
    runServer(MASTER_IP, MASTER_PORT)
    thread = threading.Thread(target=writeJsonFile, args = ())
    thread.start()
    
    # start processes
    auto_run()
    

def auto_run():
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
    
    print "LAUNCHING ALL PROCESSES"
    for player in CONF:
        addr = CONF[player]
        os.system("python ../simulation/simulator.py " + addr["IP"] + " " + addr["Port"] + " " + MASTER_IP + " " + str(MASTER_PORT) + " &")

    sleep(5)
    
    # send orders
    print "SENDING COMMANDS"
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
    
def main():
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
    
if __name__ == '__main__':
    main()
