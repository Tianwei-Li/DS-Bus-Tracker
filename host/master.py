#!/usr/bin/python   

'''
Created on Apr 5, 2014

@author: Terry Li
'''
import os
from Tkinter import *  
import host 
  
class Application(Frame):   
    def newUser(self):
        name = self.userName.get()
        ip = self.userIP.get()
        port = self.userPort.get()
        #routNo = self.queryRout.get()
        routNo = "ttt"
        interval = "50"
        #interval = self.timeInter.get()
        print "new user launched!"
        #print name + " " + ip + " " + port + " " + routNo + " " + interval 
        os.system("python gui_user.py " + ip + " " + port + " " + name + " " + routNo + " " + interval + " &")
        #host.autoInitialize(ip, int(port), name, "USER", routNo, interval)
    
    def newGSN(self):   
        name = self.gsnName.get()
        ip = self.gsnIP.get()
        port = self.gsnPort.get()
        print "new GSN launched!"  
        #print name + " " + ip + " " + port
        os.system("python gui_gsn.py " + ip + " " + port + " " + name + " &")
        
    def newDriver(self):  
        name = self.driverName.get() 
        ip = self.driverIP.get()
        port = self.driverPort.get()
        #routNo = self.routeNo.get()
        routNo = "ttt"
        print "new driver launched!"  
        #print name + " " + ip + " " + port   + " " + routNo
        os.system("python gui_driver.py " + ip + " " + port + " " + name + " " + routNo + " &")
 
 
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
        defaultPort.set("10000")
        self.userPort = Entry(self, textvariable = defaultPort)
        self.userPort.grid(row = 3, column = col+1)  
        
        '''
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
        defaultPort.set("20000")
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
        defaultPort.set("30000")
        self.driverPort = Entry(self, textvariable = defaultPort)
        self.driverPort.grid(row = 3, column = col+1) 
        '''
        Label(self, text="Route:").grid(row = 4, column = col)
        defaultRoute = StringVar()  
        defaultRoute.set("61C")
        self.routeNo = Entry(self, textvariable = defaultRoute)
        self.routeNo.grid(row = 4, column = col+1) 
        '''
        self.newDriBtn = Button(self)   
        self.newDriBtn["text"] = "launch Driver"  
        #self.newGSNBtn["fg"]   = "red"  
        self.newDriBtn["command"] =  self.newDriver   
        self.newDriBtn.grid(row = 6, column = col+1)  
           
    def createWidgets(self):
        
        Label(self, text="").grid(row = 0)
        self.createUser(0)
        self.createGSN(2)
        self.createDriv(4)
         
  
    def __init__(self, master=None):   
        Frame.__init__(self, master)   
        self.pack()   
        self.createWidgets()   
  
win = Tk()   
win.title("Master")
win.geometry("800x400")
app = Application(master=win)   
app.mainloop()   
#root.destroy()  