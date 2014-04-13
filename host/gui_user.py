'''
Host GUI Application

Created on Mar 13, 2014

@author: Qian Mao
'''

from Tkinter import Tk, BOTH
import os
import sys
import threading
import tkFileDialog
import tkSimpleDialog
from ttk import Frame, Button, Style, Label, Entry
import host
#from comm import MessagePasser


ROOT = None
APP = None
IP = None
PORT = None
LOCALNAME = None

class MainFrame(Frame):    
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()    
        # define options for opening or saving a file
              
    def initUI(self):
        self.parent.title("User Control Panel")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        self.label = Label(self, text="Mobile Live Bus Tracker", font=('Helvetica', '21'))
        self.label.grid(row=0, column=0)

        self.l = Label(self, text="My Location", font=('Helvetica', '18'))
        self.l.grid(row=1, column=0)
        self.e = Entry(self, font=('Helvetica', '18'))
        self.e.grid(row=2, column=0)

        self.l = Label(self, text="Destination", font=('Helvetica', '18'))
        self.l.grid(row=3, column=0)

        # add vertical space
        self.l = Label(self, text="", font=('Helvetica', '14'))
        self.l.grid(row=5, column=0)

        self.e = Entry(self, font=('Helvetica', '18'))
        self.e.grid(row=4, column=0)
        self.search = Button(self, text="Search")
        self.search.grid(row=6, column=0)       

        # For second screen (after user searched)
        # add vertical space
        self.l = Label(self, text="", font=('Helvetica', '14'))
        self.l.grid(row=7, column=0)

        self.l = Label(self, text="Pick a bus line", font=('Helvetica', '18'))
        self.l.grid(row=8, column=0)  
        
        self.search = Button(self, text="61A", width=40)
        self.search.grid(row=9, column=0)
        self.search = Button(self, text="61B", width=40)
        self.search.grid(row=10, column=0)
        self.search = Button(self, text="61C", width=40)
        self.search.grid(row=11, column=0)
        
        
        ############## used for debug ################
        self.l2 = Label(self, text="", font=('Helvetica', '14'))
        self.l2.grid(row=12, column=0)
        
        self.turnOnBtn = Button(self, text="Turn On")
        self.turnOnBtn["command"] = self.turnOn 
        self.turnOnBtn.grid(row=13, column=0)    
        
        self.reqBtn = Button(self, text="Request")
        self.reqBtn["command"] = self.request 
        self.reqBtn.grid(row=14, column=0)    
        
        self.turnOffBtn = Button(self, text="Turn Off")
        self.turnOffBtn["command"] = self.turnOff 
        self.turnOffBtn.grid(row=15, column=0)   
        
    def turnOn(self):
        host.enqueue({"SM":"USER_SM", "action":"turnOn", "userId":LOCALNAME, "localIP":IP, "localPort":int(PORT)})
        
    def request(self):
        host.enqueue({"SM":"USER_SM", "action":"request", "route":"71A", "direction":"north", "destination":(1,1), "location":(0,1)})
        
    def turnOff(self):
        host.enqueue({"SM":"USER_SM", "action":"turnOff"})
        
        


#    def receive(self):
        #self.label["text"] = MessagePasser.receive()
        #self.labelString.set(MessagePasser.receive())
    
#    def send(self, dst, data):
        #MessagePasser.normalSend(dst, data)
    
#    def multicast(self, group, data):
        #MessagePasser.multicast(group, data)

#def receiveThread():
#    global APP
    
#    while True:
#        APP.receive()

def main():
    global ROOT, APP
    
    host.initialize("../testFile.txt", "user", "USER", LOCALNAME, IP, int(PORT))

    ROOT = Tk()
    ROOT.geometry("320x480+300+300")
    APP = MainFrame(ROOT)
    
#    thread = threading.Thread(target=receiveThread, args = ())
#    thread.daemon = True
#    thread.start()
    
    ROOT.mainloop()  


if __name__ == '__main__':
    global IP, PORT, LOCALNAME
    
    IP = sys.argv[1]
    PORT = sys.argv[2]
    LOCALNAME = sys.argv[3]
    routNo = sys.argv[4]
    interval = sys.argv[5]
    main() 
