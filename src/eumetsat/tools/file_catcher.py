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

def find_and_copy_file(patterns, srcs, dest, copied_files_list, move):

    files_found = False
    
    for src in srcs:
        print("Info: Listing the directory %s" % (src))
        files = sorted(os.listdir(src))
        print("Info: Done Listing directory %s" % (src))
        
        for pattern in patterns:
            #print("Check %s in %s" % (the_file, src))
            for the_file in files:
                if fnmatch.fnmatch(the_file, pattern) and not (the_file in copied_files_list):
                    #shutil.copyfile('%s/%s' % (src, the_file), '%s/%s' % (dest, the_file))
                    if move:
                       shutil.move('%s/%s' % (src, the_file), '%s/%s' % (dest, the_file))
                       print("Info: Moved %s/%s in %s" % (src, the_file, dest))
                    else:
                       shutil.copyfile('%s/%s' % (src, the_file), '%s/%s' % (dest, the_file))
                       print("Info: Copied %s/%s in %s" % (src, the_file, dest))
                    files_found = True
                    copied_files_list.append(the_file)
            if not files_found:
                print("Debug: No files matching %s" % (pattern))
            else:
                files_found = False
    
    #if not files_found:
    #    print("Info: Could not find any new files matching %s" % (patterns))


def parse_args():
    """ parse arguments"""
    
    options, _ = getopt.getopt(sys.argv[1:], 'p:s:d:hwm', ['patterns=','srcs=', 
                                                             'dests=',
                                                             'help',
                                                             'wait',
                                                             'move'
                                                              ])
    #print 'OPTIONS   :', options
    help = None
    wait = False
    move = False
    sources = None
    dest = None
    patterns = None
    
    for opt, arg in options:
        if opt in ('-s', '--srcs'):
            sources = arg
        elif opt in ('-d', '--dests'):
            dest = arg
        elif opt in ('-p', '--patterns'):
            patterns = arg
            print("Patt = [%s]" % (patterns))
        elif opt in ('-w', '--wait'):
            wait = True
        elif opt in ('-m', '--move'):
            move = True
        elif opt in ('-h', '--help'):
            help = True
    
   
    if help:
        print("Usage:\n   $>python file_catcher.py -s dir-srcs -d dir-dest\n\n For example:\n   $>python file_catcher.py -s /data1,/data2 -d /tmp/results -p 'T_HH*,Z_WERT*YTR'")
        sys.exit(0)
        
    if not sources:
        print("Error: Need sources. See usage with -h")
        sys.exit(1)
    
    if not dest:
        print("Error: Need destinations. See usage with -h")
        sys.exit(1)

    if not patterns:
        print("Error: Need file patterns. See usage with -h")
        sys.exit(1)
        
    
    sources = sources.split(',')

    patterns = patterns.split(',')
    
    return sources, dest, wait, patterns , move
       

if __name__ == '__main__':
    
    srcs, dest, wait , patterns, move = parse_args()
      
    #patterns = ['T_HM*']
    seconds  = 3
    
    makedirs(dest)

    print("Info: Patterns = %s\n"%(patterns))
    
    copied_files_list = []
    
    try:
        if wait:
            print("Info: Go into waiting recurrent mode. Look for files every %s seconds\n" % (seconds))
            while True:
                find_and_copy_file(patterns, srcs, dest, copied_files_list, move)
                print("Info: Sleep %d seconds\n" % (seconds))
                time.sleep(seconds) #sleep x seconds
                
        else:
            find_and_copy_file(patterns, srcs, dest, copied_files_list, move) 
    except Exception, err:
        print(err)
        sys.exit(1)
