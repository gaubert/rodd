import sys
import zmq

import json
import threading
import time

def worker_routine(zmrl, context, i):
    
    socket = context.socket(zmq.XREQ)

    time.sleep(3)
    socket.setsockopt(zmq.IDENTITY,"w%d" % (i))
    socket.connect(zmrl)
    
    print("=W%d= Connected to %s socket.\n" %(i, zmrl))

    #send READY to server
    socket.send("READY")
    
    while True:
        #first frame is empty
        print("=W%d= Wait for some work to do.\n" % (i))
        message = socket.recv_multipart()
        print("=W%d= Got work to do. message = %s\n." % (i, message))
        time.sleep(1)
        print("=W%d= send process message back \n" %(i))
        message[-1] = "%s done" % (message[-1])
        socket.send_multipart(message)


class ZMQueue(object):
    """
    ZMQ Queue server that distribute work to workers
    Features to implement:
    - configurable priority with a score
    - priority policy module
    - message: Json metadata handler + blob
    - possibility to dynamically change the priority
    - change metadata and reorder queue
    - possibility to dequeue job and reorder it 
    - reorder by changing the priority
    - possibility to pause a job and maintain it in the queue

    """

    def __init__(self, context, q_name, in_bind_addr="tcp://127.0.0.1:6000", out_bind_addr="tcp://127.0.0.1:6001"):
        """
           in_bind_addr  : address to bind in zmq socket on
           out_bind_addr : address to bind out zmq socket
           
        """
        self._context = context
        self._in_bind_addr  = in_bind_addr
        self._out_bind_addr = out_bind_addr
        self._q_name    = q_name
        self._data = {}
        

    def start(self):

        client_socket = self._context.socket(zmq.XREP)
        client_socket.bind(self._in_bind_addr)
        client_socket.setsockopt(zmq.IDENTITY,"s_cl")
        worker_socket = self._context.socket(zmq.XREP)
        worker_socket.setsockopt(zmq.IDENTITY,"s_wo")
        worker_socket.bind(self._out_bind_addr)
        
        available_workers = 0
        workers_list      = []
        
        #set up polling methods
        #try to poll
        poller = zmq.Poller()
        poller.register(client_socket, zmq.POLLIN)
        
        poller.register(worker_socket, zmq.POLLIN)
        
        while True:
            
            time.sleep(0.5)
            print("*S* Now wait clients or workers messages.\n")
            socks = dict(poller.poll())
            
            print("*S* Got a notification")
            
            if available_workers > 0:
                #poll for workers
                if (client_socket in socks and socks[client_socket] == zmq.POLLIN):
                    #read data from client
                    message = client_socket.recv_multipart()
                    
                    print("*S* received message from client %s\n. Send it to a worker" % (message))
                    
                    available_workers -= 1
                    worker_id = workers_list.pop()
                    #send message to worker
                    worker_job = [worker_id, message[0], message[-1]]
                    worker_socket.send_multipart(worker_job)
            else:
                print("No workers available. Sleep and wait for one to be back")
                    
            if (worker_socket in socks and socks[worker_socket] == zmq.POLLIN):
                
                #first frame is empty
                message  = worker_socket.recv_multipart()
                
                if message[-1] == "READY":
                    print("*S* worker %s is ready. Add it in the list of workers ready." % (message[0]))
                    available_workers += 1
                    workers_list.append(message[0])
                    print("*S* %d workers ready to work\n" % (available_workers))
                else:
                    print("*S* received response from worker %s\n. Send it back to the client" % (message))
                    response = [message[-2], message[-1]]
                    
                    client_socket.send_multipart(response) 
                    
                    # add worker back to the list of workers
                    available_workers += 1
                    workers_list.insert(0, message[0])
                    print("worker %s ready to work again\n" % (message[0]))
                       
        

def main():
    
    zmrl = "inproc://workers"
    #zmrl = 'tcp://127.0.0.1:6005'
    context = zmq.Context(1)
    nb_workers = 10
    
    for i in range(nb_workers):
        thread = threading.Thread(target=worker_routine, args=(zmrl, context, i, ))
        thread.start()
    
    ZMQueue(context, 'queue','tcp://127.0.0.1:6000', zmrl).start()

if __name__ == "__main__":
   main()

