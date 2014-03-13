'''
Created on Mar 13, 2014

@author: Qian Mao
'''

from Tkinter import Tk, BOTH
from ttk import Frame, Button, Style


class MainFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()
        
    def initUI(self):
      
        self.parent.title("Bus Tracker")
        self.style = Style()
        self.style.theme_use("default")
        self.pack(fill=BOTH, expand=1)

        quitButton = Button(self, text="Quit", command=self.quit)
        quitButton.place(x=0, y=0)

def main():
  
    root = Tk()
    root.geometry("250x250+300+300")
    app = MainFrame(root)
    root.mainloop()  


if __name__ == '__main__':
    main() 