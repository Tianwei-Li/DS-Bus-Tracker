'''
Created on Apr 9, 2014

@author: Qian Mao
'''

class BusTableElm:
    def __init__(self, routeName, direction, busId, location, addr):
        self.routeName = routeName
        self.direction = direction
        self.busId = busId
        self.location = location
        self.addr = addr