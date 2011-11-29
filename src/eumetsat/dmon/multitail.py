'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''
import time
import select
import fcntl
import os

from stat import ST_SIZE


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
    def check_file_rotation(cls, file_list, file_sizes):
        """
           Check if the files have rotated and reopen the new file if necessary
           return a type ( file_list, corresponding file_size ) 
        """
        size = -1
        
        res_flist = []
        res_fsize = []
        
        for ind in xrange(0, len(file_list)):
            name = file_list[ind].name
            size = os.path.getsize(name)
            #file is smaller so it rotated
            #reopen it
            if size < file_sizes[ind]:
                file_list[ind].close()
                fdesc = open(name,'r')
                res_flist.append(fdesc)
                res_fsize.append(os.path.getsize(name))
            else:
                #update list
                res_flist.append(file_list[ind])
                res_fsize.append(size)
                
        return (res_flist, res_fsize)
            
    @classmethod
    def tail(cls, a_files, delay=0.4):
        """\
        Iterator generator that returns lines as data is added to the file.

        Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
        
        Return (line, filename)
        """
        trailing = True
        sizes    = []
        
        # go the end of file
        for the_file in a_files:
            
            # get file size and store it in sizes
            sizes.append(os.path.getsize(the_file.name))
            #go the end of files
            the_file.seek(0,2) 
            #set it non blocking
            file_num = the_file.fileno()
            old_flags = fcntl.fcntl(file_num, fcntl.F_GETFL)
            fcntl.fcntl(file_num, fcntl.F_SETFL, old_flags | os.O_NONBLOCK)    
        
        
        select_iteration = 0
        while 1:
            #set up the select (for the moment use a select)
            (rlist, _, _) = select.select(a_files, [], [], 1)
            
            select_iteration +=1
            
            if len(rlist) > 0:
                for a_file in rlist:
                    #try to read up to x lines
                    nb_line_max_to_read = 10
                    line_read = 0
                    while line_read < nb_line_max_to_read:
                        where = a_file.tell()
                        line = a_file.readline()
                        if line:    
                            if trailing and line in MultiFileTailer.LINE_TERMINATORS:
                                # This is just the line terminator added to the end of the file
                                # before a new line, ignore.
                                trailing = False
                                #leave readline loop to continue next iteration of file reading loop
                                break
            
                            if line[-1] in MultiFileTailer.LINE_TERMINATORS:
                                line = line[:-1]
                                if line[-1:] == '\r\n' and '\r\n' in MultiFileTailer.LINE_TERMINATORS:
                                    # found crlf
                                    line = line[:-1]
            
                            trailing = False
                            line_read +=1
                            yield (line, os.path.basename(a_file.name)) 
                        else:
                            trailing = True
                            a_file.seek(where)
                            time.sleep(delay)
                            
                            #every ten iteration check that has not rotated
                            if select_iteration > 15:
                                (a_files, res_fsize) = MultiFileTailer.check_file_rotation(a_files, sizes)
                                select_iteration = 0
                            
                            #leave line reading loop
                            break
            else:
                time.sleep(delay)
                (a_files, res_fsize) = MultiFileTailer.check_file_rotation(a_files, sizes)
   
        
        
        
        

if __name__ == '__main__':

    file_send = open('/tmp/logfile.log')
    #file_send = open('/tmp/weather.txt')
    file_send1 = open('/tmp/weather.txt')
    file_send2 = open('/tmp/weather.txt')

    lines = MultiFileTailer.tail([file_send, file_send1, file_send2])

    for line in lines:
        print(line)
