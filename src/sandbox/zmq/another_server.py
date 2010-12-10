'''
Created on Dec 10, 2010

@author: gaubert
'''
 

import zmq
import sys


# call this script like this: server.py addr

address = 'tcp://127.0.0.1:6006'
context = zmq.Context()
socket = context.socket(zmq.XREP)
socket.setsockopt(zmq.IDENTITY,"server")
socket.bind(address)

cpt = 0
while True:
    msg = socket.recv_multipart()
    print("Received %s\n" %(msg))
    
    if msg[-1] == "READY":
        #send job to do
        msg[-1] = "JOB %d" %(cpt)
    else:
        #received the following
        print("Error received something I don't understand so send it back")
    
    socket.send_multipart(msg)