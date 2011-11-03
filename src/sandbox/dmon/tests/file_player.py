'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''
import time

def play_file(source_f, dest_f, a_sleep_time):
    """
       play a file
    """
    
    
    for line in source_f:
        dest_f.write(line)
        dest_f.flush()
        time.sleep(a_sleep_time)

if __name__ == '__main__':
    
    source_f = open('/homespace/gaubert/logs/tests/send.log')
    dest_f   = open('/tmp/dest.log','w+')
    play_file(source_f, dest_f, 0.5)