"""

   Broker peering simulation (part 2)
   Prototypes the request-reply flow
 
   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>
  
"""
import threading
import time
import zmq

import os,sys
import sys
import termios
from sandbox.zmq.lruqueue import NBR_WORKERS


NBR_CLIENTS = 10
NBR_WORKERS = 3


def getchar():
    """
       taken from http://snippets.dzone.com/posts/show/3084
       Equivale al comando getchar() di C
       
    """

    fd = sys.stdin.fileno()
    
    if os.isatty(fd):
        
        old = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
        new[6] [termios.VMIN] = 1
        new[6] [termios.VTIME] = 0
        
        try:
            termios.tcsetattr(fd, termios.TCSANOW, new)
            termios.tcsendbreak(fd,0)
            ch = os.read(fd,7)

        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, old)
    else:
        ch = os.read(fd,7)
    
    return(ch)


def client_thread(context):
    """ Request-reply client using REQ socket """
    
    socket = context.socket(zmq.REQ)
    
    socket.connect("inproc://localfe")

    while True:
        #  Send request, get reply
        socket.send_multipart(["HELLO"])
        
        message = socket.recv_multipart()
        
        print("I: client status: %s\n", message)


def worker_thread(context):
    """ Worker using REQ socket to do LRU routing """
    
    socket = context.socket(zmq.REQ)
    
    socket.connect("inproc://localbe")
    
    # Tell the borker we are ready for work
    socket.send("READY")
    
    try:
        while True:
            
            zmsg = socket.recv_multipart()
            
            # Do some 'work'
            time.sleep(1)
               
            zmsg.append("OK - %04x" % (0x10000))
            
            socket.send_multipart(zmsg)
            
    except zmq.ZMQError, zerr:
        # context terminated so quit silently
        if zerr.strerror == 'Context was terminated':
            return
        else:
            raise zerr

def main():
    """ main method """
    
    self  = ""
    peers = [] 
    
    # Prepare our context and sockets
    context = zmq.Context(1)
    
    # Bind cloud frontend to endpoint
    cloudfe = context.socket(zmq.XREP)
    endpoint = "ipc://%s-cloud.ipc" % (self)
    cloudfe.setsockopt(zmq.IDENTITY, self) #set identity
    cloudfe.bind(endpoint)
    
    # Connect cloud backend to all peers
    cloudbe = context.socket(zmq.XREP)
    cloudbe.setsockopt(zmq.IDENTITY, self) #set identity
    
    for peer in peers:
        print("I: connecting to cloud frontend at '%s'\n" %(peer))
        endpoint = "ipc://%s-cloud.ipc" % (peer)
        cloudbe.connect(endpoint)
    
    # Prepare local frontend and backend
    localfe = context.socket(zmq.XREP) 
    localfe.bind("inproc://localfe")
    localbe = context.socket(zmq.XREP)
    localbe.bind("inproc://localbe")
    
    # Get user to tell us when we can start...
    print("Press Enter when all brokers are started: ")
    getchar()
    
    # create workers and clients threads
    for _ in range(NBR_WORKERS):
        thread = threading.Thread(target=worker_thread, args=(context))
        thread.start()
    
    for _ in range(NBR_CLIENTS):
        thread_c = threading.Thread(target=client_thread, args=(context))
        thread_c.start()
    
    # Interesting part
    # -------------------------------------------------------------
    # Request-reply flow
    # - Poll backends and process local/cloud replies
    # - While worker available, route localfe to local or cloud

    # Queue of available workers
    capacity = 0
    worker_queue = []
    
    # init poller
    poller = zmq.Poller()
    
    poller.register(localbe, zmq.POLLIN)
    poller.register(cloudbe, zmq.POLLIN)
    
    while True:
        
        #  If we have no workers anyhow, wait indefinitely
        backends = dict(poller.poll( (1000000 if capacity else None) ))
        
        # Handle reply from local worker
        if localbe in backends and backends[localbe] == zmq.POLLIN:
        
            zmsg = localbe.recv_multipart()
            
            assert capacity < NBR_WORKERS
           
            # Use worker address for LRU routing
            worker_addr = zmsg[0]
            
            # add worker back to the list of available workers
            capacity += 1
            worker_queue.append(worker_addr)
            
            client_addr = zmsg[1]
            
            # If client reply, send rest back to frontend
            if client_addr != "READY":
                zmsg = []
                
        # Or handle reply from peer broker
        elif cloudbe in backends and backends[cloudbe] == zmq.POLLIN: 
            zmsg = cloudbe.recv_multipart()
            # We don't use peer broker address for anything
            zmsg = []
        
        # Route reply to cloud if it's addressed to a broker
        for peer in peers:
            if zmsg[1] == peer:
                cloudfe.send(zmsg)
        
        # Route reply to client if we still need to
        if zmsg:
            localfe.send(zmsg)
        
        
        # Now route as many clients requests as we can handle
        #
        # init poller
        poller = zmq.Poller()
        poller.register(localfe, zmq.POLLIN)
        poller.register(cloudfe, zmq.POLLIN)
        
        
        while capacity:
            #  If we have no workers anyhow, wait indefinitely
            frontends = dict(poller.poll())
            
            reroutable = 0
            
            # We'll do peer brokers first, to prevent starvation
            if cloudfe in frontends and frontends[cloudfe] == zmq.POLLIN: 
                zmsg = cloudfe.recv_multipart()
                reroutable = 0
            elif localfe in frontends and frontends[localfe] == zmq.POLLIN: 
                zmsg = localfe.recv_multipart()
                reroutable = 1
            else:
                break # No work, go back to backends
            
            # If reroutable, send to cloud 20% of the time
            # Here we'd normally use cloud status information
            #
            if reroutable and len(peer) > 2 :
                # Route to random broker peer
                #random_peer = 
            
            """
            TO BE DONE
            // If reroutable, send to cloud 20% of the time
            // Here we'd normally use cloud status information
            //
            if (reroutable && argc > 2 && within (5) == 0) {
                // Route to random broker peer
                int random_peer = within (argc - 2) + 2;
                zmsg_wrap (zmsg, argv [random_peer], NULL);
                zmsg_send (&zmsg, cloudbe);
            }
            else {
                zmsg_wrap (zmsg, worker_queue [0], "");
                zmsg_send (&zmsg, localbe);

                // Dequeue and drop the next worker address
                free (worker_queue [0]);
                DEQUEUE (worker_queue);
                capacity--;
            }
            """
 
           
  
    

if __name__ == "__main__":
    
    #process args
    
    main()


