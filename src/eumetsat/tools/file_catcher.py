'''
Created on Feb 7, 2012

@author: guillaume.aubert@eumetsat.int
'''

import re
import os
import shutil
import time
import fnmatch
import sys
import getopt

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
            #print("Check %s in %s" % (the_file, src))
            for pattern in patterns:
                if fnmatch.fnmatch(the_file, pattern) and not (the_file in copied_files_list):
                    #shutil.copyfile('%s/%s' % (src, the_file), '%s/%s' % (dest, the_file))
                    shutil.move('%s/%s' % (src, the_file), '%s/%s' % (dest, the_file))
                    print("Info: Moved %s/%s in %s" % (src, the_file, dest))
                    files_found = True
                    copied_files_list.append(the_file)
    
    if not files_found:
        print("Info: Could not find any new files matching %s" % (pattern))


def parse_args():
    """ parse arguments"""
    
    options, _ = getopt.getopt(sys.argv[1:], 's:d:hw', ['srcs=', 
                                                             'dests=',
                                                             'help',
                                                             'wait'
                                                              ])
    #print 'OPTIONS   :', options
    help = None
    wait = False
    sources = None
    dest = None
    
    for opt, arg in options:
        if opt in ('-s', '--srcs'):
            sources = arg
        elif opt in ('-d', '--dests'):
            dest = arg
        elif opt in ('-w', '--wait'):
            wait = True
        elif opt in ('-h', '--help'):
            help = True
    
   
    if help:
        print("Usage:\n   $>python file_catcher.py -s dir-srcs -d dir-dest\n\n For example:\n   $>python file_catcher.py -s /data/data_share -d /tmp/results")
        sys.exit(0)
        
    if not sources:
        print("Error: Need sources. See usage with -h")
        sys.exit(1)
    
    if not dest:
        print("Error: Need sources. See usage with -h")
        sys.exit(1)
        
    
    sources = sources.split(',')
    
    return sources, dest, wait
       

if __name__ == '__main__':
    
    srcs, dest, wait = parse_args()
      
    patterns = ['T_HM*']
    seconds  = 3
    
    makedirs(dest)
    
    copied_files_list = []
    
    try:
        if wait:
            print("Info: Go into waiting recurrent mode. Look for files every %s seconds\n" % (seconds))
            while True:
                find_and_copy_file(patterns, srcs, dest, copied_files_list)
                print("Info: Sleep %d seconds\n" % (seconds))
                time.sleep(seconds) #sleep x seconds
                
        else:
            find_and_copy_file(patterns, srcs, dest, copied_files_list) 
    except Exception, err:
        print(err)
        sys.exit(1)
