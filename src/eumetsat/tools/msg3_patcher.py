'''
Created on Nov 14, 2012

@author: guillaume.aubert@eumetsat.int
'''

import shutil
import os

def dirwalk(dir):
    """
     Walk a directory tree, using a generator.
     This implementation returns only the files in all the subdirectories.
     Beware, this is a generator.
    """
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath):  # recurse into subdir
                yield x
        else:
            yield fullpath

def modify_file(filepath):
    """
       change the file and rename it
    """
    
    print("==== Try to modify %s ====\n" % (filepath))
    
    fd = open(filepath, "r+b")
    
    # look for @ within the next 200 bytes
    byte_pos = 0
    found = False
    
    while byte_pos < 200:
        val = fd.read(1)
        byte_pos +=1
        if val == '@':
            val = fd.read(1) #check that next byte is L or H and reposition file index
            fd.seek(byte_pos)
            if val in ('H', 'L'):
                found = True
                break
    
    
    
    if not found:
        raise Exception("Error was expecting @ in offset hex 12 and got %s" % (val))
    
    read_filename = fd.read(61) #read filename 
    
    if read_filename != os.path.basename(filepath):
        raise Exception("Error wrong filename Was expecting %s and read %s" % (os.path.basename(filepath), read_filename))
    
    #print("read filename = %s\n" %(read_filename))
    par_pos = read_filename.find("_PAR____")
    
    if par_pos >= 0:
        print("Overwrite filename value in file %s" % (filepath))
        fd.seek(byte_pos + par_pos)
        fd.write("________")
        fd.close()
    
        # rename file
        dir, name = os.path.split(filepath)
        name = name.replace("_PAR____", "________")
        shutil.move(filepath, "%s/%s" % (dir, name))
    else:
        print("IGNORE %s. No _PAR____ detected." % (filepath))
        fd.close()
    
    


if __name__ == '__main__':
    
    src_dir  = "/homespace/gaubert/msg3-data/H"
    dest_dir = "/tmp/msg3-test"
    
    for filepath in dirwalk(src_dir):         
        shutil.copy(filepath, dest_dir)
        modify_file('%s/%s' % (dest_dir, os.path.basename(filepath)))