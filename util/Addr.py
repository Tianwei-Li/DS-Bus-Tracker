'''
Created on Apr 9, 2014

@author: Qian Mao
'''

class Addr:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        
    def __repr__(self):
        return "%s:%s" % (self.ip, self.port)