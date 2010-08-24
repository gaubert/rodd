'''
Created on Aug 23, 2010

@author: guillaume.aubert@eumetsat.int
'''

import os
import fnmatch

def file_exits(a_file_path):
    """
       Check a file exist and send an exception if it doesn't
    
        Args:
           a_file_path: file_path to check
           
        Returns:
          Nothing
           
        Except:
          Exception if file doesn't exits 
    """
    # asserting input parameters
    if a_file_path == None:
        raise Exception(-1, "passed argument aFilePath is null")
    else:
        # check if file exits
        if not os.path.exists(a_file_path):
            raise Exception(-1, "the file %s does not exits" % (a_file_path))
        
def makedirs(a_path):
    """
       make all dirs that do not exists i the path.
       If all dirs alrealdy exists return without any errors
    
        Args:
           a_path: path of dirs to create
           
        Returns:
          Nothing
           
        Except:
          OSError if the dirs cannot be created for some reasons, 
    """
    
    if os.path.isdir(a_path):
        # it already exists so return
        return
    elif os.path.isfile(a_path):
        raise OSError("a file with the same name as the desired dir, '%s', already exists." % (a_path))

    os.makedirs(a_path)
    
def __rmgeneric(path, __func__):
    """ private function that is part of delete_all_under """
    try:
        __func__(path)
        #print 'Removed ', path
    except OSError, (_, strerror): #IGNORE:W0612
        print """Error removing %(path)s, %(error)s """ % {'path' : path, 'error': strerror }
            
def delete_all_under(a_path, a_delete_top_dir=False):
    """
        Delete all files and dirs that are under a_path
    
        Args:
           a_path           : top dir from where to delete
           a_delete_top_dir : delete top dir as well
           
        Returns:
          Nothing
           
        Except:
          OSError if the dirs cannot be created for some reasons, 
    """

    if not os.path.isdir(a_path):
        return
    
    files = os.listdir(a_path)

    for p_elem in files:
        fullpath = os.path.join(a_path, p_elem)
        if os.path.isfile(fullpath):
            the_func = os.remove
            __rmgeneric(fullpath, the_func)
        elif os.path.isdir(fullpath):
            delete_all_under(fullpath)
            the_func = os.rmdir
            __rmgeneric(fullpath, the_func)
    
    if a_delete_top_dir:
        os.rmdir(a_path)


def dirwalk(a_dir, a_wildcards= '*'):
    """
     Walk a directory tree, using a generator.
     This implementation returns only the files in all the subdirectories.
     Beware, this is a generator.
     
     Args:
         a_dir: A root directory from where to list
         a_wildcards: Filtering wildcards a la unix
    """
   
    for the_file in fnmatch.filter(sorted(os.listdir(a_dir)), a_wildcards):
        fullpath = os.path.join(a_dir, the_file)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for p_elem in dirwalk(fullpath, a_wildcards):  # recurse into subdir
                yield p_elem
        else:
            yield fullpath
