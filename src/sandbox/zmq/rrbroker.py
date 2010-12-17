"""

   Simple request-reply broker
 
   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>
  
"""
import zmq

int main (int argc, char *argv[])
{
    // Prepare our context and sockets
    void *context = zmq_init (1);
    void *frontend = zmq_socket (context, ZMQ_XREP);
    void *backend = zmq_socket (context, ZMQ_XREQ);
    zmq_bind (frontend, "tcp://*:5559");
    zmq_bind (backend, "tcp://*:5560");

    // Initialize poll set
    zmq_pollitem_t items [] = {
        { frontend, 0, ZMQ_POLLIN, 0 },
        { backend, 0, ZMQ_POLLIN, 0 }
    };
    // Switch messages between sockets
    while (1) {
        zmq_msg_t message;
        int64_t more; // Multipart detection

        zmq_poll (items, 2, -1);
        if (items [0].revents & ZMQ_POLLIN) {
            while (1) {
                // Process all parts of the message
                zmq_msg_init (&message);
                zmq_recv (frontend, &message, 0);
                size_t more_size = sizeof (more);
                zmq_getsockopt (frontend, ZMQ_RCVMORE, &more, &more_size);
                zmq_send (backend, &message, more? ZMQ_SNDMORE: 0);
                zmq_msg_close (&message);
                if (!more)
                    break; // Last message part
            }
        }
        if (items [1].revents & ZMQ_POLLIN) {
            while (1) {
                // Process all parts of the message
                zmq_msg_init (&message);
                zmq_recv (backend, &message, 0);
                size_t more_size = sizeof (more);
                zmq_getsockopt (backend, ZMQ_RCVMORE, &more, &more_size);
                zmq_send (frontend, &message, more? ZMQ_SNDMORE: 0);
                zmq_msg_close (&message);
                if (!more)
                    break; // Last message part
            }
        }
    }
    // We never get here but clean up anyhow
    zmq_close (frontend);
    zmq_close (backend);
    zmq_term (context);
    return 0;
}

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
                message = []
                
                frontend.append(frontend.recv())
                
                more = frontend.getsockopt(zmq.RCVMORE)
                
                frontend.send(message, more ? zmq.SNDMORE: 0)
                
                if not more:
                    break # Last message part

    # We never get here but clean up anyhow
    zmq_close (frontend);
    zmq_close (backend);
    zmq_term (context);
    return 0;








if __name__ == "__main__":
    main()