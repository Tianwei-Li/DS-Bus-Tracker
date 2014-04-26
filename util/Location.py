'''
Created on Apr 25, 2014

@author: Qian Mao
'''

LOCATION = 0
LIMIT = 30

def setLocation(location):
    global LOCATION
    LOCATION = location

def getLocation():
    global LOCATION
    return LOCATION

def clear():
    global LOCATION
    LOCATION = 0
    
def moveOneStop():
    global LOCATION, LIMIT
    if LOCATION < LIMIT - 1:
        LOCATION = LOCATION + 1
    
