'''
Created on Feb 7, 2012

@author: guillaume.aubert@eumetsat.int
'''

import re
import os
import shutil
import time
import fnmatch

def makedirs(aPath):
    """ my own version of makedir """
    
    if os.path.isdir(aPath):
        # it already exists so return
        return
    elif os.path.isfile(aPath):
        raise OSError("a file with the same name as the desired dir,'%s', already exists."%(aPath))
    
    os.makedirs(aPath)

def find_and_copy_file(patterns, srcs, dest, copied_files_list):

    files_found = False
    
    for src in srcs:
        files = os.listdir(src)
        
        for the_file in files:
            print("Check %s in %s" % (the_file, src))
            for pattern in patterns:
                if fnmatch.fnmatch(the_file, pattern) and not (the_file in copied_files_list):
                    shutil.copyfile('%s/%s' % (src, the_file), '%s/%s' % (dest, the_file))
                    print("Copied %s/%s in %s" % (src, the_file, dest))
                    files_found = True
                    copied_files_list.append(the_file)
    
    if not files_found:
        print("Could not find any new files matching %s" % (pattern))





if __name__ == '__main__':

   #src  = '/home/eumetman/data/eumetcast/BMD-RA-VI/'
   srcs  = ['/tmp/test/']
   dest = '/tmp/results'
   patterns = ['R?D*']

   makedirs(dest)

   copied_files_list = []
   while True:
       find_and_copy_file(patterns, srcs, dest, copied_files_list)
       print("sleep 2 seconds\n")
       time.sleep(2) #sleep 2 seconds