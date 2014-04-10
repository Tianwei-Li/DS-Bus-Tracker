'''
Created on Apr 9, 2014

@author: Qian Mao
'''

class RouteTableElm:
    def __init__(self, routeName, rsnAddr, busTable):
        self.rsnAddr = rsnAddr
        self.routeName = routeName
        self.busTable = busTable