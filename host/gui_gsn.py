'''
Driver GUI Application

Created on Mar 13, 2014

@author: Terry Li
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
GSNID = None

class MainFrame(Frame):    
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()    
              
    def initUI(self):
        self.parent.title("GSN Control Panel")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        self.turnOnBtn = Button(self, text="Turn On")
        self.turnOnBtn["command"] = self.turnOn 
        self.turnOnBtn.grid(row=0, column=0)    
        
        self.turnOffBtn = Button(self, text="Turn Off")
        self.turnOffBtn["command"] = self.turnOff 
        self.turnOffBtn.grid(row=0, column=1)   
    
    def turnOn(self):
        host.enqueue({"SM":"GSN_SM", "action":"turnOn", "gsnId":GSNID, "localIP":IP, "localPort":int(PORT)})
        
    def turnOff(self):
        host.enqueue({"SM":"GSN_SM", "action":"turnOff"})
        
def main():
    global ROOT, APP
    host.initialize(LOCALNAME, "GSN", GSNID, IP, int(PORT))
    ROOT = Tk()
    ROOT.geometry("320x480+300+300")
    APP = MainFrame(ROOT)
      
    ROOT.mainloop()  


if __name__ == '__main__':
    global IP, PORT, LOCALNAME, GSNID
    
    IP = sys.argv[1]
    PORT = sys.argv[2]
    LOCALNAME = sys.argv[3]
    GSNID = "id" + LOCALNAME
    main() 
