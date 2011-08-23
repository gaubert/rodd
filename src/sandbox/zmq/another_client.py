'''
Created on Dec 10, 2010

@author: gaubert
'''
import zmq
import sys
import time


# Call start the client like this: python client.py addr1 addr2

# ------------------------------------------------------------------------------

def send(socket, msg, depth=0, max_depth=4, timeout=0.9):
    '''Nonblocking send noticing server deaths. Sends a message and waits for
``timeout`` seconds for a reply, in case no reply is received, the message is resent
'''
    socket.send(msg)
    t = time.time()
    while True:
        try:
            #reply = socket.recv(zmq.NOBLOCK)
            reply = socket.recv()
        except zmq.ZMQError, e:
            if e.errno == zmq.EAGAIN:
                # no message was ready
                if depth == max_depth:
                    raise Exception("max depth reached")
                if time.time() >= t + timeout:
                    # no message was received for ``timeout`` seconds
                    return send(socket, msg, depth+1)
            else:
                raise # real error
        else:
            return reply
    

# ------------------------------------------------------------------------------

#servers = sys.argv[1:]
servers = ['tcp://127.0.0.1:6006']
context = zmq.Context()
socket = context.socket(zmq.XREQ)
i = 0
socket.setsockopt(zmq.IDENTITY,"w%d" % (i))
for addr in servers:
    socket.connect(addr)

for i in range(0, 10):
    reply = send(socket, "msg " + str(i))
    print reply