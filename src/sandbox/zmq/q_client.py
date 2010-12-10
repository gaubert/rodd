'''
Created on Dec 8, 2010

@author: gaubert
'''

import json
import zmq

class MongoZMQClient(object):
    """
Client that connects with MongoZMQ server to add/fetch docs
"""

    def __init__(self, i, connect_addr='tcp://127.0.0.1:6000'):
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.XREQ)
        self._socket.setsockopt(zmq.IDENTITY,"c%d" % (i))
        self._socket.connect(connect_addr)

    def send(self, msg):
        """ send msg """
        self._socket.send(msg)
    
    def recv(self):
        """ recv msg """
        return self._socket.recv()

    def _send_recv_msg(self, msg):
        self._socket.send(msg)
        return self._socket.recv()

def main():
   
    i = 1
    client = MongoZMQClient(i)
    
    
    doc = {'key': 'doc%d'%(i), 'job': str(i)}
    work_batch = "work batch %d"
    
    for i in range(10):
        client.send(work_batch %(i))
        msg = client.recv()
        print("received %s\n" %(msg))


if __name__ == "__main__":
    main()

