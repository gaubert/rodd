'''
Created on 5 Jul 2010

@author: guillaume.aubert@eumetsat.int
'''

USAGE="""Usage:
cygwin_launch python_program project_srcs [working_directory]

Parameters:
python_program: The python programm to launch with cygwin python.

project_srcs  : The root directory of the project python sources. 
                In general it will be under workspace/proj_name/src.
                Several path can be added if separated by :.

working_directory (not implemented): The working directory from where to start. 

"""
if __name__ == '__main__':
    
    import sys
    # first get the parameters
    # 1: python file to exec
    # 2: project sources to add in path (could have multiples then they are separated by :
    # 3: Future change working dir if necessary
    
    if len(sys.argv) <= 2:
        print("Error. Need at least 2 arguments.\n%s" %(USAGE))
        exit(1)
    elif len(sys.argv) == 3:
        python_program    = sys.argv[1]
        project_root_srcs = sys.argv[2]
        working_dir       = None
    elif len(sys.argv) == 4:
        python_program    = sys.argv[1]
        project_root_srcs = sys.argv[2]
        working_dir       = sys.argv[3]
    
    # add project source root in PYTHONPATH
    sys.path.append(project_root_srcs)
    
    #maybe change working directory
    #import os
    #os.chdir('/cygdrive/h/Dev/ecli-workspace/rodd/src')
    
    print("exec %s\n" %(python_program))
    
    execfile(python_program)
    
    exit(0)
    
    
    
    
    
    