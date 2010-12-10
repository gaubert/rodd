'''
Created on Dec 9, 2010

@author: gaubert
'''


import sys
import zmq

import json
import threading
import time



def main():
    
    zmrl = 'tcp://127.0.0.1:6005'
    i = 0
    context = zmq.Context()
    
    socket = context.socket(zmq.XREP)
    socket.setsockopt(zmq.IDENTITY,"server")
    socket.bind(zmrl)
    
    print("=ss%d= Connected to %s socket.\n" %(i, zmrl))
    
    cpt = 0
    while True:
        msg = socket.recv_multipart()
        print("Received %s\n" %(msg))
        
        if msg[-1] == "READY":
            #send job to do
            msg[-1] = "JOB %d" %(cpt)
            cpt +=1
        else:
            #received the following
            print("Error received something I don't understand so send it back")
    
        socket.send_multipart(msg)
        
    
if __name__ == "__main__":
    main()
