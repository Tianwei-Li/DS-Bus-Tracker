'''
Created on Apr 25, 2014

@author: Qian Mao
'''
import sys
sys.path += ['../']

import comm.TCPComm as TCPComm
from time import sleep

CONF = {
        "GSN" : "127.0.0.1:9000",
        "DRIVER_1" : "127.0.0.1:9100",
        "DRIVER_2" : "127.0.0.1:9200",
        "DRIVER_3" : "127.0.0.1:9300"
        }

if __name__ == "__main__":
    
    file = open("../feedFile.txt", "r")
    for line in file:
        # skip blank lines
        if not line.strip():
            continue

        # ignore comment
        if line.startswith("#"):
            continue
        
        # print line
        tokens = line.split(' ', 1)
        addr = CONF[tokens[0]].split(':')
        message = eval(tokens[1])
        ip = addr[0]
        port = int(addr[1])
        TCPComm.send(ip, port, message)


