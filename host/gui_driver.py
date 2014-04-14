'''
Driver GUI Application

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
              
    def initUI(self):
        self.parent.title("Driver Control Panel")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        self.label = Label(self, text="Bus Tracker - Driver", font=('Helvetica', '21'))
        self.label.grid(row=0, column=0)

        self.l = Label(self, text="Bus Line", font=('Helvetica', '18'))
        self.l.grid(row=1, column=0)
        self.e = Entry(self, font=('Helvetica', '18'))
        self.e.grid(row=2, column=0)

        self.l = Label(self, text="Direction", font=('Helvetica', '18'))
        self.l.grid(row=3, column=0)

        # add vertical space
        self.l = Label(self, text="", font=('Helvetica', '14'))
        self.l.grid(row=5, column=0)

        self.e = Entry(self, font=('Helvetica', '18'))
        self.e.grid(row=4, column=0)
        self.search = Button(self, text="Start")
        self.search.grid(row=6, column=0)   
        
        
        ######### used for debug ##########
        # add vertical space
        self.l2 = Label(self, text="", font=('Helvetica', '14'))
        self.l2.grid(row=5, column=0)
        
        self.turnOnBtn = Button(self, text="Turn On")
        self.turnOnBtn["command"] = self.turnOn 
        self.turnOnBtn.grid(row=6, column=0)    
        
        self.startBtn = Button(self, text="Start")
        self.startBtn["command"] = self.start 
        self.startBtn.grid(row=7, column=0)    
        
        self.turnOffBtn = Button(self, text="Turn Off")
        self.turnOffBtn["command"] = self.turnOff 
        self.turnOffBtn.grid(row=8, column=0)   
        
    def turnOn(self):
        host.enqueue({"SM":"DRIVER_SM", "action":"turnOn", "busId":LOCALNAME, "localIP":IP, "localPort":int(PORT)})
        
    def start(self):
        host.enqueue({"SM":"DRIVER_SM", "action":"start", "route":"71A", "direction":"north", "location":(0,0)})
        
    def turnOff(self):
        host.enqueue({"SM":"DRIVER_SM", "action":"turnOff"})    

def main():
    global ROOT, APP
    
    host.initialize("../testFile.txt", "driver1", "DRIVER", LOCALNAME, IP, int(PORT))
    ROOT = Tk()
    ROOT.geometry("320x480+300+300")
    APP = MainFrame(ROOT)
      
    ROOT.mainloop()  


if __name__ == '__main__':
    global IP, PORT, LOCALNAME
    
    IP = sys.argv[1]
    PORT = sys.argv[2]
    LOCALNAME = sys.argv[3]
    routNo = sys.argv[4]
    main() 
