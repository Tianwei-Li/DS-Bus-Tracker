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

CONF = {
        "GSN" : "127.0.0.1:9000",
        "DRIVER_1" : "127.0.0.1:9100",
        "USER_1" : "127.0.0.1:10000"
        }

TCP_IP = '127.0.0.1'
TCP_PORT = 60000
#import google_map


NODES = None
LINKS = None
DIC = None
BUSCNT = None
ROUTTABLE = None

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
    def getIdxByName(self, name):
        for i in range(len(NODES)):
            if NODES[i]["name"] == name:
                return NODES[i]["index"]
        
        return 0
    
    def writeJsonFile(self, name, type, busLine):
        dic = {}
        dic["index"] = len(NODES)
        dic["name"] = name
        dic["type"] = type
        if type == "gsn":
            dic["fixed"] = "true"
            dic["x"] = 480
            dic["y"] = 40
        
        if type == "DRIVER" or type == "RSN":
            dic["fixed"] = "true"
            dic["x"] = ROUTTABLE[busLine][0]["x"]
            dic["y"] = ROUTTABLE[busLine][0]["y"]
            
        NODES.append(dic)
        
        if type != "gsn":
            dic = {}
            dic["index"] = len(LINKS)
            if (type == "DRIVER"):
                rsnName = "RSN-" + busLine
                dic["source"] = self.getIdxByName(rsnName)
            else:
                dic["source"] = 0
            dic["target"] = len(NODES) - 1
            LINKS.append(dic)
        
        self.outfile = open("../visualization/graph.json", "w")
        json.dump(DIC, self.outfile)
        self.outfile.close()
        
        
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
        
        '''
        Label(self, text="Query Interval:").grid(row = 5, column = col)
        defaultInterv = StringVar()
        defaultInterv.set("10 s")
        self.timeInter = Entry(self, textvariable = defaultInterv)
        self.timeInter.grid(row = 5, column = col+1) 
        '''
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
    
    def setupSim(self):
        addr = CONF["GSN"].split(':')
        os.system("python ../simulation/simulator.py " + addr[0] + " " + addr[1] + " &")
        addr = CONF["DRIVER_1"].split(':')
        os.system("python ../simulation/simulator.py " + addr[0] + " " + addr[1] + " &")
        addr = CONF["USER_1"].split(':')
        os.system("python ../simulation/simulator.py " + addr[0] + " " + addr[1] + " &")
        #addr = CONF["DRIVER_3"].split(':')
        #os.system("python ../simulation/simulator.py " + addr[0] + " " + addr[1] + " &")
        #addr = CONF["USER_1"].split(':')
        #os.system("python ../simulation/simulator.py " + addr[0] + " " + addr[1] + " &")

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
            tokens = line.split(' ', 1)
            addr = CONF[tokens[0]].split(':')
            message = eval(tokens[1])
            if (message["action"] == "initialize"):
                self.writeJsonFile(message["localName"], message["role"], "61A")
            ip = addr[0]
            port = int(addr[1])
            TCPComm.send(ip, port, message)
           
    def createWidgets(self):
        global NODES, LINKS, DIC, BUSCNT
        NODES = []
        LINKS = []
        DIC = {}
        DIC["nodes"] = NODES
        DIC["links"] = LINKS
        
        BUSCNT = {}
        
        Label(self, text="").grid(row = 0)
        self.createUser(0)
        self.createGSN(2)
        self.createDriv(4)
        
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
    json_data = open('coordinates.json')
    ROUTTABLE = json.load(json_data)


def updateNodePos(name, busLine, idx):
    node = getNodeByName(name)
    if node != None:
        node["x"] = ROUTTABLE[busLine][idx]["x"]
        node["y"] = ROUTTABLE[busLine][idx]["y"]

    


def updateJsonFile():
    
    while True:
        if MSG_QUEUE:
            command = MSG_QUEUE.popleft()
            for item in command.items():
                updateNodePos(item[0], "61A", item[1])
            outfile = open("../visualization/graph.json", "w")
            json.dump(DIC, outfile)
            outfile.close()
            
            locationFile = open("../visualization/locList.txt", "w")
            for elm in NODES:
                locationFile.write(elm["name"] + " " + elm["x"] + " " + elm["y"] + "\n")
            locationFile.close()
            time.sleep(5)
            
    '''
    rout61File = "rout61.json"
    rout71File = "rout71.json"
    with FileLock(rout61File):
        json_data = open(rout61File)
        rout61Bus = json.load(json_data)
        for item in rout61Bus.items():
            updateNodePos(item[0], "61A", item[1])
            
        
    with FileLock(rout71File):
        json_data = open(rout71File)
        rout71Bus = json.load(json_data)
        for item in rout71Bus.items():
            updateNodePos(item[0], "71B", item[1])
    '''
    
    
def main():
    readRoutTable()
    
    global MSG_QUEUE, TCP_IP, TCP_PORT


    runServer(TCP_IP, TCP_PORT)
    thread = threading.Thread(target=updateJsonFile, args = ())
    thread.start()
    win = Tk()   
    win.title("Master")
    win.geometry("800x400")
    app = Application(master=win)   
    app.mainloop()   
    #root.destroy()  
    
if __name__ == '__main__':
    main()
