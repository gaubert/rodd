'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int

@version: 1.1.1-2012-01-03T11:55:00
'''
import time
import select
import fcntl
import os
import sys

import StringIO
import traceback

def get_exception_traceback():
    """
            return the exception traceback (stack info and so on) in a string
        
            Args:
               None
               
            Returns:
               return a string that contains the exception traceback
        
            Raises:
               
    """
   
    the_file = StringIO.StringIO()
    exception_type, exception_value, exception_traceback = sys.exc_info() #IGNORE:W0702
    traceback.print_exception(exception_type, exception_value, exception_traceback, file = the_file)
    return the_file.getvalue()

class MultiFileTailer(object):
    '''
       Does a tail on multiple files
    '''
    
    LINE_TERMINATORS  = ('\r\n', '\n', '\r')
    READ_BUFFER       = 8192 #read by block of X bits max
    SELECT_ITERATIONS = 25   #number of iteration before to check if file has rotated


    def __init__(self,):
        '''
        Constructor
        '''
        pass
    
    @classmethod
    def check_file_rotation(cls, file_list, file_sizes):
        """
           Check if the files have rotated and reopen the new file if necessary.
           Rotates only if there nothing else to read in the current file
           return a type ( file_list, corresponding file_size ) 
        """
        res_flist = []
        res_fsize = []
        
        for ind in xrange(0, len(file_list)):
            name = file_list[ind].name
            
            curr_pos = file_list[ind].tell()
            
            # get total file size to see if the file has changed: rotation
            curr_file_size = os.path.getsize(name)
            
            # if there are still thing to read size > curr_pos
            #file with the same name is smaller so it rotated
            #reopen it only if there are no more to read on current one
            if curr_file_size < file_sizes[ind]: #file rotated
                
                # check that there if no more to read
                #go to end pos of the open file to have its size
                file_list[ind].seek(0, 2)
                end_of_curr_file_pos = file_list[ind].tell()
                
                #reposition to real curr_pos
                file_list[ind].seek(curr_pos)
                
                #open new file if no more to read
                if end_of_curr_file_pos <= curr_pos:
                    file_list[ind].close()
                    fdesc = open(name,'r')
                    res_flist.append(fdesc)
                    res_fsize.append(os.path.getsize(name))
                else:
                    #update list
                    res_flist.append(file_list[ind])
                    res_fsize.append(end_of_curr_file_pos)
                    
            else:
                #update list
                res_flist.append(file_list[ind])
                res_fsize.append(curr_file_size)
                
        return (res_flist, res_fsize)
            
    @classmethod
    def tail(cls, a_files, delay=0.4, go_to_the_end = True):
        """\
        Iterator generator that returns lines as data is added to the file.

        Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
        
        Return (line, filename)
        """
        sizes          = []
        file_buffer    = {}
        
        # go the end of file
        for the_file in a_files:
            
            # get file size and store it in sizes
            sizes.append(os.path.getsize(the_file.name))
            
            if go_to_the_end:
                #go the end of files
                the_file.seek(0, 2) 
            
            #set it non blocking
            file_num = the_file.fileno()
            old_flags = fcntl.fcntl(file_num, fcntl.F_GETFL)
            fcntl.fcntl(file_num, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)  
            
            #initialise file position
            file_buffer[the_file.name] = ''  
        
        
        select_iteration = 0
        while 1:
            #set up the select (for the moment use a select)
            (rlist, _, _) = select.select(a_files, [], [], 1)
            
            select_iteration += 1
            
            if len(rlist) > 0:
                for a_file in rlist:              
                    data = a_file.read(cls.READ_BUFFER)
                    if len(data) < 1: #no more to read
                        #check if file has rotated
                        if select_iteration > cls.SELECT_ITERATIONS:#every x iterations check that has not rotated
                            (a_files, sizes) = MultiFileTailer.check_file_rotation(a_files, sizes)
                            select_iteration = 0
                        continue
                    
                    file_buffer[a_file.name] = file_buffer[a_file.name] + data
                    
                    #  process lines within the data
                    while 1:
                        pos = file_buffer[a_file.name].find('\n')
                        if pos < 0: break #pylint: disable-msg=C0321
                        the_line = file_buffer[a_file.name][:pos]
                        file_buffer[a_file.name] = file_buffer[a_file.name][pos + 1:]
                        
                        yield(the_line, os.path.basename(a_file.name))
            else:
                (a_files, sizes) = MultiFileTailer.check_file_rotation(a_files, sizes)
            
            time.sleep(delay) #sleep time to no eat all resources
   
        
def usage():
    """
       print usage
    """
    print >> sys.stderr, "multitail.py file1 file2 file3 file4"
        

if __name__ == '__main__':
    
    files = []
        

    try:
        #open files
        for file in sys.argv:
            files.append(open(file, 'r'))
    
        for line in MultiFileTailer.tail(files):
            print >> sys.stdout, line
            
    except KeyboardInterrupt:
            #CTRL^C pressed so silently quit
            pass
    except Exception, exc:
        print >> sys.stderr, exc
        print >> sys.stderr, 'exception traceback: %s' % (get_exception_traceback())
        sys.exit(1) 
    
    sys.exit(0)
