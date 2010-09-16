'''
Created on Feb 2, 2010

@author: guillaume.aubert@ctbto.org

function for dynamically loading a module

'''

import hashlib
import imp

from org.eumetsat.conf.exceptions import Error

def load(a_module_name, a_src_dir):
    ''' load a module 
        a_code_path : name of the module to load
        a_src_dir   : from where to read it
    '''
    try:
        
        #create module path by replacing all . with / and addinf .py
        pathname = '%s/%s.py' % ( a_src_dir, a_module_name.replace('.', '/') )
        
        fin = open(pathname, 'rb')

        try:
            the_md5 = hashlib.md5()
            the_md5.update(pathname)
            return  imp.load_source(the_md5.hexdigest(), pathname, fin)
        finally:
            try: fin.close()
            except: pass
    except Exception, x:
        #traceback.print_exc(file = sys.stderr)
        raise Error("Problem to load module %s. Error: %s" % (a_module_name, x) )

def _find_module(a_name_list, a_current_module=None):
    ''' Recursive find module func as it isn't done by the module imp '''
    if len(a_name_list) <= 0:
        return a_current_module
    
    # get first element
    name = a_name_list.pop(0)
    
    m = _load(name, (a_current_module.__path__ if a_current_module else None) )
    
    return _find_module(a_name_list,m)

def _load(a_name):
    ''' load a module '''

    name_list = a_name.split('.')
    
    return _find_module(name_list)

