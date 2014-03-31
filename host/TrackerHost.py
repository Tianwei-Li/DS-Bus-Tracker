'''
Host GUI Application

Created on Mar 13, 2014

@author: Qian Mao
'''

from Tkinter import Tk, BOTH
import os
import threading
import tkFileDialog
import tkSimpleDialog
from ttk import Frame, Button, Style, Label

from comm import MessagePasser


ROOT = None
APP = None

class MainFrame(Frame):    
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
        
        # define options for opening or saving a file
        self.file_opt = options_file = {}
        options_file['defaultextension'] = '.txt'
        options_file['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        options_file['initialdir'] = '../'
        options_file['initialfile'] = 'testFile'
        options_file['parent'] = self.parent
        options_file['title'] = 'Choose configuration file'
        
        # define options for asking local name
        self.ask_localname_opt = options_localName = {}
        options_localName['parent'] = self.parent
        options_localName['initialvalue'] = "alice"
        
        conf = tkFileDialog.askopenfilename(**self.file_opt)
        localName = tkSimpleDialog.askstring("local name", "Please enter your name:", **self.ask_localname_opt)
        
        MessagePasser.initialize(conf, localName)
        

        
    def initUI(self):
        self.parent.title("Bus Tracker")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        self.label = Label(self, text="Ready")
        self.label.grid(row=0, column=0)
        # TEST ONLY
        self.testButton = Button(self, text="Send", command= lambda: self.send("alice", "hi alice"))
        self.testButton.grid(row=1, column=0)
        self.testButton = Button(self, text="Multicast", command= lambda: self.multicast("group1", "hi group1"))
        self.testButton.grid(row=1, column=1)
        self.quitButton = Button(self, text="Quit", command=self.quit)
        self.quitButton.grid(row=1, column=2)
        
        
    def receive(self):
        self.label["text"] = MessagePasser.receive()
        #self.labelString.set(MessagePasser.receive())
    
    def send(self, dst, data):
        MessagePasser.normalSend(dst, data)
    
    def multicast(self, group, data):
        MessagePasser.multicast(group, data)

def receiveThread():
    global APP
    
    while True:
        APP.receive()

def main():
    global ROOT, APP
    
    ROOT = Tk()
    ROOT.geometry("250x250+300+300")
    APP = MainFrame(ROOT)
    
    thread = threading.Thread(target=receiveThread, args = ())
    thread.daemon = True
    thread.start()
    
    ROOT.mainloop()  


if __name__ == '__main__':
    main() 