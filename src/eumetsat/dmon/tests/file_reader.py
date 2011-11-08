'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''
import time
import select
import fcntl
import os

def tail(f, n, offset=None):
    """Reads a n lines from f with an offset of offset lines.  The return
    value is a tuple in the form ``(lines, has_more)`` where `has_more` is
    an indicator that is `True` if there are more lines in the file.
    """
    avg_line_length = 130
    to_read = n + (offset or 0)

    while 1:
        try:
            f.seek(-(avg_line_length * to_read), 2)
        except IOError:
            # woops.  apparently file is smaller than what we want
            # to step back, go to the beginning instead
            f.seek(0)
        pos = f.tell()
        lines = f.read().splitlines()
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None], \
                   len(lines) > to_read or pos > 0
        avg_line_length *= 1.3

line_terminators = ('\r\n', '\n', '\r')

def follow(a_files, delay=0.4):
        """\
        Iterator generator that returns lines as data is added to the file.

        Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
        """
        trailing = True  
        
        # go the end of file
        for the_file in a_files:
            #go the end of files
            the_file.seek(0,2) 
            #set it non blocking
            #file_num = the_file.fileno()
            #old_flags = fcntl.fcntl(file_num, fcntl.F_GETFL)
            #fcntl.fcntl(file_num, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)    
        
        while 1:
            
            #set up the select (for the moment use a select)
            (rlist, wlist, _) = select.select(a_files, [], [], 1)
            
            if len(rlist) > 0:
                for a_file in rlist:
                    where = a_file.tell()
                    line = a_file.readline()
                    if line:    
                        if trailing and line in line_terminators:
                            # This is just the line terminator added to the end of the file
                            # before a new line, ignore.
                            trailing = False
                            continue
        
                        if line[-1] in line_terminators:
                            line = line[:-1]
                            if line[-1:] == '\r\n' and '\r\n' in line_terminators:
                                # found crlf
                                line = line[:-1]
        
                        trailing = False
                        print("****************name = %s\n***************" % (a_file.name) )
                        yield line
                    else:
                        trailing = True
                        a_file.seek(where)
                        print("sleep in readline\n")
                        time.sleep(delay)
            else:
                print("sleep in select\n")
                time.sleep(delay)

def first_version_go_back_to_the_file():
    file_send  = open('/tmp/dest.log')
    file_send1 = open('/tmp/dest1.log')
    
    offset   = 0
    nb_lines = 10
    
    has_more = True
    
    while True:
        while has_more:
            (lines, has_more) = tail(file_send, nb_lines, offset)
            offset += len(lines)
            print("Has more (%s) : offset (%s)\n" % (has_more, offset))
            for line in lines:
               print(line)
        
        #no more to read sleep
        print('no more to read sleep\n')
        time.sleep(2)


if __name__ == '__main__':
    
    file_send = open('/tmp/dest.log')
    file_send1 = open('/tmp/dest1.log')
    
    lines = follow([file_send, file_send1])
    
    for line in lines:
        print(line)
    
    