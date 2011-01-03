"""

   Simple request-reply broker
 
   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>
  
"""
import zmq



def main():
    """ main method """
    
    # Prepare our context and sockets
    context = zmq.Context(1)
    frontend = context.socket(zmq.XREP)
    frontend.bind("tcp://*:5559")
    backend = context.socket(zmq.XREQ)
    backend.bind("tcp://*:5560")

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(backend, zmq.POLLIN)
    poller.register(frontend, zmq.POLLIN)
    
    while True:
        
        socks = dict(poller.poll())
        
        # poll frontend
        if (frontend in socks and socks[frontend] == zmq.POLLIN):
            while True:
                # Process all parts of the message
                message = frontend.recv()
                
                more = frontend.getsockopt(zmq.RCVMORE)
                
                backend.send(message, zmq.SNDMORE if more else 0)
                
                if not more:
                    break # Last message part
        if (backend in socks and socks[backend] == zmq.POLLIN):
            while True:
                # Process all parts of the message
               
                
                message = backend.recv()
                
                more = backend.getsockopt(zmq.RCVMORE)
                
                frontend.send(message, zmq.SNDMORE if more else 0)
                
                if not more:
                    break # Last message part

    # We never get here but clean up anyhow
    frontend.close()
    backend.close()
    context.term()

if __name__ == "__main__":
    main()