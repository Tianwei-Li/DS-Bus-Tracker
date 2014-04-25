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
        # response = sock.recv(1024)
        # print "Received: {}".format(response)
    finally:
        sock.close()
        
if __name__ == "__main__":
    
    # client("localhost", 9999, "123")
    
    message_init_driver = {"action" : "initialize",
                           "localName" : "dirver_alice",
                           "role" : "DRIVER",
                           "id" : "bus_71A_alice",
                           "localIP" : "127.0.0.1",
                           "localPort" : 41000
                           }
    message_init_gsn = {"action" : "initialize",
                        "localName" : "gsn_1",
                        "role" : "GSN",
                        "id" : "gsn_pittsburgh_1",
                        "localIP" : "127.0.0.1",
                        "localPort" : 40000
                        }
    message_exit = {"action" : "exit"
                    }
    TCPComm.send("localhost", 9999, message_exit)
    
