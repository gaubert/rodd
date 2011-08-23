'''
Created on Jan 10, 2011

@author: guillaume.aubert@eumetsat.int
'''

import re
import sys
import time



def network_feed(device,rxtx):
    """network_feed(device,rxtx) -> function that returns given device stream speed
    rxtx is "RX" or "TX"
    """
    assert rxtx in ["RX","TX"]
    r = re.compile(r"^\s*" + re.escape(device) + r":(.*)$", re.MULTILINE)
    
    def networkfn(devre=r,rxtx=rxtx):
        f = open('/proc/net/dev')
        dev_lines = f.read()
        f.close()
        match = devre.search(dev_lines)
        if not match:
            return None
        
        parts = match.group(1).split()
        if rxtx == 'RX':
            return long(parts[0])
        else:
            return long(parts[8])
        
    return networkfn

class NetworkTap:
    def __init__(self, rxtx, interface):
        self.ftype = rxtx
        self.interface = interface
        self.feed = network_feed(interface, rxtx)
    
    def description(self):
        return self.ftype+": "+self.interface

    def wait_creation(self):
        if self.feed() is None:
            sys.stdout.write("Waiting for network statistics from "
                "interface '%s'...\n" % self.interface)
            while self.feed() == None: 
                time.sleep(1)

def convert_bytes(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size

class Watcher:
    
    def __init__(self, incoming, outgoing):
        
        self.incoming = NetworkTap("RX",incoming)
        self.outgoing = NetworkTap("RX",outgoing)
        
    def watch(self):
        " watch "
        
        prev_incoming = self.incoming.feed()
        prev_outgoing = self.outgoing.feed()
        
        rec_in  = 0
        rec_out = 0
        
        elapsed = 0
        start = time.time()

        prev_time = start
        
        
        while True:
            
            time.sleep(1)
            
            inc  = self.incoming.feed()
            out  = self.outgoing.feed()
            
            rec_in  += (inc - prev_incoming)
            rec_out += (out - prev_outgoing)
            prev_incoming = inc
            prev_outgoing = out
            
            curr_time = time.time()
            elapsed  += curr_time - prev_time
            prev_time = curr_time
            
            print("incoming received %s\n" % (rec_in) )
            
            print("outgoing received %s\n" % (rec_out) )
            
            print("difference %s\n" % (rec_out - rec_in))
            
            print("elapsed %s\n" % (elapsed))
            
            print("incoming rate  = %s/s\n" % (convert_bytes(rec_in/elapsed)) )
        

if __name__ == "__main__":
    
    watcher = Watcher("eth0","eth0")
    
    watcher.watch()