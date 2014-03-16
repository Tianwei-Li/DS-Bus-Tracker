'''
Created on Mar 15, 2014

@author: Qian Mao
'''

holdBackQueue = []
# key is message src+seq
msgStateMap = {}

# called by MessagePasser, if the received message is multicast message
def offer(message):
    # check if the message is new
    msgStateMap[m]