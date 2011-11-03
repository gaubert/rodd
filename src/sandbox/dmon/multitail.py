'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''
import time
import select
import fcntl
import os

class MultiFileTailer(object):
    '''
       Does a tail on multiple files
    '''
    
    LINE_TERMINATORS = ('\r\n', '\n', '\r')


    def __init__(self,):
        '''
        Constructor
        '''
        pass
        
    @classmethod
    def tail(cls, a_files, delay=0.4):
        """\
        Iterator generator that returns lines as data is added to the file.

        Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
        
        Return (line, filename)
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
            (rlist, _, _) = select.select(a_files, [], [], 1)
            
            if len(rlist) > 0:
                for a_file in rlist:
                    where = a_file.tell()
                    line = a_file.readline()
                    if line:    
                        if trailing and line in MultiFileTailer.LINE_TERMINATORS:
                            # This is just the line terminator added to the end of the file
                            # before a new line, ignore.
                            trailing = False
                            continue
        
                        if line[-1] in MultiFileTailer.LINE_TERMINATORS:
                            line = line[:-1]
                            if line[-1:] == '\r\n' and '\r\n' in MultiFileTailer.LINE_TERMINATORS:
                                # found crlf
                                line = line[:-1]
        
                        trailing = False
                        yield (line, a_file.name)
                    else:
                        trailing = True
                        a_file.seek(where)
                        time.sleep(delay)
            else:
                time.sleep(delay)