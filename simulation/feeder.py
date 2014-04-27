'''
Created on Apr 25, 2014

@author: Qian Mao
'''
import sys
sys.path += ['../']

import comm.TCPComm as TCPComm
from time import sleep

CONF = {}

'''
        "GSN" : "127.0.0.1:9000",
        "DRIVER_1" : "127.0.0.1:9100",
        "DRIVER_2" : "127.0.0.1:9200",
        "DRIVER_3" : "127.0.0.1:9300",
        "USER_1" : "127.0.0.1:10000"
'''
if __name__ == "__main__":
    
    file = open("../feedFile.txt", "r")
    for line in file:
        global CONF
        # skip blank lines
        if not line.strip():
            continue

        # ignore comment
        if line.startswith("#"):
            continue
        
        # print line
        line = line.rstrip()
        if line.startswith("CONF"):
            tokens = line.split(' ')
            CONF[tokens[1]] = {"IP" : tokens[2], "Port" : tokens[3]}
        else:
            tokens = line.split(' ', 1)
            message = eval(tokens[1])
            ip = CONF[tokens[0]]["IP"]
            port = int(CONF[tokens[0]]["Port"])
            TCPComm.send(ip, port, message)


