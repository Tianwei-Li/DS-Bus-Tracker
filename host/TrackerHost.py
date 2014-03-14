'''
Host GUI Application

Created on Mar 13, 2014

@author: Qian Mao
'''

import threading

from comm import MessagePasser
from Tkinter import Tk, BOTH
from ttk import Frame, Button, Style, Label

ROOT = None
APP = None

class MainFrame(Frame):    
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
        
        MessagePasser.initialize("../testFile", "alice")
        
    def initUI(self):
        self.parent.title("Bus Tracker")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        self.label = Label(self, text="Ready")
        self.label.grid(row=0, column=0)
        self.testButton = Button(self, text="Test", command=self.receive)
        self.testButton.grid(row=1, column=0)
        self.quitButton = Button(self, text="Quit", command=self.quit)
        self.quitButton.grid(row=1, column=1)
        
        
    def receive(self):
        self.label["text"] = MessagePasser.receive()
        #self.labelString.set(MessagePasser.receive())

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