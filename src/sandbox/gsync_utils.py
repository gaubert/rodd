'''
Created on Dec 1, 2011

@author: guillaume.aubert@gmail.com
'''
import os

def makedirs(aPath):
    """ my own version of makedir """
    
    if os.path.isdir(aPath):
        # it already exists so return
        return
    elif os.path.isfile(aPath):
        raise OSError("a file with the same name as the desired dir, '%s', already exists."%(aPath))

    os.makedirs(aPath)

def __rmgeneric(path, __func__):
    """ private function that is part of delete_all_under """
    try:
        __func__(path)
        #print 'Removed ', path
    except OSError, (errno, strerror): #IGNORE:W0612
        print """Error removing %(path)s, %(error)s """%{'path' : path, 'error': strerror }
            
def delete_all_under(path,delete_top_dir=False):
    """ delete all files and directories under path """

    if not os.path.isdir(path):
        return
    
    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            f=os.remove
            __rmgeneric(fullpath, f)
        elif os.path.isdir(fullpath):
            delete_all_under(fullpath)
            f=os.rmdir
            __rmgeneric(fullpath, f)
    
    if delete_top_dir:
        os.rmdir(path)