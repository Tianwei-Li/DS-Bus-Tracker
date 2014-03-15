'''
Socket level communication utility

Created on Mar 11, 2014

@author: Qian Mao
'''
import SocketServer
import collections
import logging
import socket
import threading


logging.basicConfig()
LOGGER = logging.getLogger("TCPComm")
LOGGER.setLevel(logging.DEBUG)

# deque for buffering received messages
RECVMSGQUE = collections.deque()

# tcp server for receiving
server = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        RECVMSGQUE.append(data)
        LOGGER.info("Receive message from %s : %s", self.request.getpeername(), data)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# Initialize tcp server for receiving
def runServer(ip, port):
    LOGGER.info("Lisenting on (%s, %d)", ip, port)
    
    global server
    
    server = ThreadedTCPServer((ip, port), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

# Get the topmost message received and deliver
def receive():
    if RECVMSGQUE:
        return RECVMSGQUE.popleft()
    else:
        return None

# Send the message to destination
def send(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
    finally:
        sock.close()
    LOGGER.info("Send message to (%s, %d) : %s", ip, port, message)

# shutdown tcp server for receiving
def shutdown():
    server.shutdown()

if __name__ == "__main__":
    runServer("localhost", 9999)
    count = 0
    while True:
        send("localhost", 9999, "fuck")
        msg = receive()
        if msg:
            print msg
            count = count + 1
        if count == 3:
            break
    shutdown()