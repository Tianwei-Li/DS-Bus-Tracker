'''
Driver GUI Application

Created on Mar 13, 2014

@author: Qian Mao
'''

from Tkinter import Tk, BOTH
import os
import threading
import tkFileDialog
import tkSimpleDialog
from ttk import Frame, Button, Style, Label, Entry

ROOT = None
APP = None

class MainFrame(Frame):    
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()    
              
    def initUI(self):
        self.parent.title("Mobile Live Bus Tracker")
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

def main():
    global ROOT, APP
    
    ROOT = Tk()
    ROOT.geometry("320x480+300+300")
    APP = MainFrame(ROOT)
      
    ROOT.mainloop()  


if __name__ == '__main__':
    main() 
