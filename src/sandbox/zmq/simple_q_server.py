import sys
import zmq

import json
import threading
import time

NBR_WORKERS = 25

def worker_routine(zmrl, context, i):
    """ worker thread routine """
    
    socket = context.socket(zmq.REQ)

    identity = "w%d" % (i)
    
    socket.setsockopt(zmq.IDENTITY, identity) #set worker identity
    
    time.sleep(2)
    
    socket.connect(zmrl)
    
    print("=w%d= Connected to %s socket.\n" %(i, zmrl))

    # Tell the borker we are ready for work
    socket.send("READY")
    
    while True:
        
        # read id, empty frame and work to do
        id = socket.recv()
        
        empty = socket.recv()
        
        assert empty == ""
        
        work_to_do = socket.recv()
        
        print("w%d. Work to do %s\n" %(work_to_do))
        
        socket.send(identity)
        socket.send("")
        socket.send("OK")
        
def client_routine(zmrl, context, i):
    """ client thread routine """
    
    socket = context.socket(zmq.REQ)

    identity = "c%d" % (i)
    
    socket.setsockopt(zmq.IDENTITY, identity) #set worker identity
    
    time.sleep(2)
    
    socket.connect(zmrl)
    
    print("c%d. Connected to %s socket.\n" %(i, zmrl))

    # Tell the borker we are ready for work
    socket.send("HELLO")
    
    reply = socket.recv()
    
    print("c%d. %s\n" % (reply))
    
    return


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

    def __init__(self, context, q_name, in_bind_addr="tcp://127.0.0.1:6000", out_bind_addr="tcp://127.0.0.1:6001", client_nbr=10):
        """
           in_bind_addr  : address to bind in zmq socket on
           out_bind_addr : address to bind out zmq socket
           
        """
        self._context = context
        self._in_bind_addr  = in_bind_addr
        self._out_bind_addr = out_bind_addr
        self._q_name    = q_name
        self._client_nbr = client_nbr
        

    def start(self):

        front_end = self._context.socket(zmq.XREP)
        front_end.bind(self._in_bind_addr)
        front_end.setsockopt(zmq.IDENTITY,"s_cl")
        back_end = self._context.socket(zmq.XREP)
        back_end.setsockopt(zmq.IDENTITY,"s_wo")
        back_end.bind(self._out_bind_addr)
        
        available_workers = 0
        workers_list      = []
        
        #set up polling methods
        #try to poll
        poller = zmq.Poller()
        poller.register(front_end, zmq.POLLIN)
        
        poller.register(back_end, zmq.POLLIN)
        
        while True:
            
            time.sleep(0.5)
            print("*S* Now wait clients or workers messages.\n")
            socks = dict(poller.poll())
            
            print("*S* Got a notification")
            
            if available_workers > 0:
                #poll for workers
                if (front_end in socks and socks[front_end] == zmq.POLLIN):
                    #read data from client
                    
                    client_addr = front_end.recv()
                    
                    empty = front_end.recv()
                    
                    assert empty == ""
                    
                    request = front_end.recv()
                    
                    available_workers -= 1
                    worker_id = workers_list.pop()
                    
                    front_end.send(worker_id)
                    front_end.send("")
                    front_end.send(client_addr)
                    front_end.send(request)
            else:
                print("No workers available. Sleep and wait for one to be back")
                    
            if (back_end in socks and socks[back_end] == zmq.POLLIN):
                
                # Queue worker address for LRU routing
                worker_addr  = back_end.recv()
                
                assert available_workers < NBR_WORKERS
                
                # add worker back to the list of workers
                available_workers += 1
                workers_list.append(worker_addr)
                
                #second frame is empty
                empty = back_end.recv()
                assert empty == ""
                
                # Third frame is READY or else a client reply address
                client_addr = back_end.recv()
                
                # If client reply, send rest back to frontend
                if client_addr != "READY":
                    
                    #second frame is empty
                    empty = back_end.recv()
                    assert empty == ""
                    
                    reply = back_end.recv()
                    
                    front_end.send(client_addr)
                    front_end.send("")
                    front_end.send(reply)
                    
                    self._client_nbr -= 1
                    
                    if self._client_nbr == 0:
                        break #Exit after N messages
    
        #out of infinite loop: do some housekeeping
        time.sleep (1)
        front_end.close()
        back_end.close()
        
    
        
def main():
    
    zmrl_worker = "inproc://workers"
    #zmrl = 'tcp://127.0.0.1:6005'
    zmrl_client = "inproc://clients"
    
    context = zmq.Context(1)
    
    nb_workers = 1
    
    nb_clients = 1
    
    
    for i in range(nb_workers):
        thread = threading.Thread(target=worker_routine, args=(zmrl_worker, context, i, ))
        thread.start()
    
    for i in range(nb_clients):
        thread_c = threading.Thread(target=client_routine, args=(zmrl_client, context, i, ))
        thread_c.start()
    
    ZMQueue(context, 'lru_queue', zmrl_client, zmrl_worker, nb_clients).start()

if __name__ == "__main__":
   main()

