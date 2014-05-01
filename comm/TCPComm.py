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
import pickle
'''
logging.basicConfig()
LOGGER = logging.getLogger("TCPComm")
LOGGER.setLevel(logging.DEBUG)
'''
LOGGER = logging.getLogger("Simulator")

# deque for buffering received messages
RECVMSGQUE = collections.deque()
LOCALNAME = ""
SEQ_NUM = 0

# tcp server for receiving
TCP_SERVER = None

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = pickle.loads(self.request.recv(4096))
        message = data["data"]
        RECVMSGQUE.append(message)
        LOGGER.info("Receive message from %s : %s", self.request.getpeername(), data)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# Initialize tcp server for receiving
def runServer(ip, port, localName):
    LOGGER.info("Lisenting on (%s, %d)", ip, port)
    
    global TCP_SERVER, LOCALNAME
    
    LOCALNAME = localName
    
    TCP_SERVER = ThreadedTCPServer((ip, port), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=TCP_SERVER.serve_forever)
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
    global LOCALNAME, SEQ_NUM
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    packet = { "src" : LOCALNAME,
               "dst_ip" : ip,
               "dst_port" : port,
               "seq" : SEQ_NUM,
               "data" : message}
    try:
        sock.connect((ip, port))
        sock.sendall(pickle.dumps(packet))
    except socket.error as e:
        LOGGER.error("Socket error: " + str(e))
        return
    finally:
        sock.close()
        
    SEQ_NUM = SEQ_NUM + 1
    LOGGER.info("Send message to (%s, %d) : %s", ip, port, packet)

# shutdown tcp server for receiving
def shutdown():
    TCP_SERVER.shutdown()

if __name__ == "__main__":
    runServer("localhost", 9999, "alice")
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