'''
TEST

Socket level client for test only

Created on Mar 12, 2014

@author: Qian Mao
'''

import socket
import TCPComm


def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        #response = sock.recv(1024)
        #print "Received: {}".format(response)
    finally:
        sock.close()
        
if __name__ == "__main__":
    #client("localhost", 20000, "")
    message = {"type" : "NORMAL",
               "src" : "GSN",
               "seq" : None,
               "group" : None,
               "memberList" : [],
               "data" : "GSN_USER_ACK"
               }
    TCPComm.send("localhost", 20000, message)