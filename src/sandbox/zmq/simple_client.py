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
    
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.IDENTITY,"w%d" % (i))
    
    socket.connect(zmrl)
    
    
    print("=W%d= Connected to %s socket.\n" %(i, zmrl))

    #send READY to server
    socket.send("READY")

    while True:
        #first frame is empty
        print("=W%d= Wait for some work to do.\n" % (i))
        message = socket.recv()
        print("=W%d= Got work to do. message = %s\n." % (i, message))
        #time.sleep(1)
        print("=W%d= send process message back \n" %(i))
        socket.send("READY")

if __name__ == "__main__":
    main()