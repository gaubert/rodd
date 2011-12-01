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
        trailing       = True
        sizes          = []
        file_buffer    = {}
        
        # go the end of file
        for the_file in a_files:
            
            # get file size and store it in sizes
            sizes.append(os.path.getsize(the_file.name))
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
            
            select_iteration +=1
            
            if len(rlist) > 0:
                for a_file in rlist:              
                    data = a_file.read(4096)
                    if len(data) < 1:
                        continue
                    
                    file_buffer[a_file.name] = file_buffer[a_file.name] + data
                    
                    #  process lines within the data
                    while 1:
                        pos = file_buffer[a_file.name].find('\n')
                        if pos < 0: break
                        the_line = file_buffer[a_file.name][:pos]
                        file_buffer[a_file.name] = file_buffer[a_file.name][pos + 1:]
                        
                        yield(the_line, os.path.basename(a_file.name))
                    
                        
                    #every ten iteration check that has not rotated
                    if select_iteration > 15:
                        (a_files, sizes) = MultiFileTailer.check_file_rotation(a_files, sizes)
                        select_iteration = 0
                        
                        #leave line reading loop
                        break
            else:
                time.sleep(delay)
                (a_files, sizes) = MultiFileTailer.check_file_rotation(a_files, sizes)
   
        
        
        
        

if __name__ == '__main__':

    file_send = open('/tmp/analyse/logfile.log')
    #file_send = open('/tmp/weather.txt')
    file_send1 = open('/tmp/weather.txt')
    file_send2 = open('/tmp/weather.txt')

    lines = MultiFileTailer.tail([file_send, file_send1, file_send2])

    for line in lines:
        print(line)
