'''
Created on Jan 31, 2012

@author: guillaume.aubert@eumetsat.int
'''
import os
import fnmatch
import tarfile
import re
import sys
from  shutil import copyfile


class Chdir:         
    def __init__( self, newPath ):  
        self.savedPath = os.getcwd()
        os.chdir(newPath)

    def __del__( self ):
        os.chdir( self.savedPath )
        
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
        
def copy_tree(src, dst):
    """Copy an entire directory tree 'src' to a new location 'dst'.

    Both 'src' and 'dst' must be directory names.  If 'src' is not a
    directory, raise DistutilsFileError.  If 'dst' does not exist, it is
    created with 'mkpath()'.  The end result of the copy is that every
    file in 'src' is copied to 'dst', and directories under 'src' are
    recursively copied to 'dst'.  Return the list of files that were
    copied or might have been copied, using their output name.  The
    return value is unaffected by 'update' or 'dry_run': it is simply
    the list of all files under 'src', with the names changed to be
    under 'dst'.

    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be
    copied as symlinks (on platforms that support them!); otherwise
    (the default), the destination of the symlink will be copied.
    'update' and 'verbose' are the same as for 'copy_file'.
    """
    if not os.path.isdir(src):
        raise Exception, \
              "cannot copy tree '%s': not a directory" % src
    try:
        names = os.listdir(src)
    except os.error, (_, errstr):
            raise Exception, \
                  "error listing files in '%s': %s" % (src, errstr)

    makedirs(dst)

    outputs = []

    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        if os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            
            os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os.path.isdir(src_name):
            outputs.extend(copy_tree(src_name, dst_name))
        else:
            copyfile(src_name, dst_name)
            
            outputs.append(dst_name)

    return outputs


def dirwalk(a_dir, a_wildcards= '*'):
    """
     Walk a directory tree, using a generator.
     This implementation returns only the files in all the subdirectories.
     Beware, this is a generator.
     
     Args:
         a_dir: A root directory from where to list
         a_wildcards: Filtering wildcards a la unix
    """

    #iterate over files in the current dir
    for the_file in fnmatch.filter(sorted(os.listdir(a_dir)), a_wildcards):
        fullpath = os.path.join(a_dir, the_file)
        if not os.path.isdir(fullpath):
            yield fullpath
    
    sub_dirs = os.walk(a_dir).next()[1]
    #iterate over sub_dirs
    for sub_dir in sub_dirs:
        fullpath = os.path.join(a_dir, sub_dir)
        for p_elem in dirwalk(fullpath, a_wildcards):
            yield p_elem 
    
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


def extract_all(tarobj):
    """
       To implement for python 2.4 and being compliant with PUMA python version
    """
    for member in tarobj.getmembers():
        tarobj.extract(member)
    
    
NCEP_PREFIX="ncep_forecast"
#FILENAME_PATTERN="ncep_forecast_(?P<date>\d{8})_\S*.tar"
FILENAME_PATTERN="ncep_forecast_(?P<date>\d{8})_africa.html"
FILENAME_RE = re.compile(FILENAME_PATTERN)


def process_ncep_tars(input_dir, working_dir, output_dir):
    """
       Process NCEP tars
    """
    makedirs(output_dir)
    makedirs(working_dir)
    
    #cd to working dir
    cd = Chdir(working_dir)
    
    matched = FILENAME_RE.match('ncep_forecast_20120719_africa.html')
    if matched:
        print("date = %s\n" %(matched.group("date")))

    sys.exit(1)

    copyfile('%s/africa.html' % (input_dir), '%s/africa.html' % (output_dir))
    
    for full_path in dirwalk(input_dir, "*.tar"):
        print("The file %s\n" % (full_path))
        tar = tarfile.open(full_path)
        #tar.extractall()
        extract_all(tar)
        tar.close()
        
        # get basename
        (bname, ext) = os.path.splitext(os.path.basename(full_path))
    
        #print("filename = %s, ext = %s\n" % (bname, ext))
        
        # if basename finished with _1 then copy content under
        if bname.endswith('_1'):
            destination = '%s/%s' % (output_dir, bname[:bname.find('_1')])
        else:
            # make dest dir if not created
            destination = '%s/%s' % (output_dir, bname)
        
        makedirs(destination)

        copy_tree('%s/%s' % (working_dir, bname), destination)

        

if __name__ == '__main__':
    #input_dir, working_dir, output_dir
    #process_ncep_tars('/homespace/gaubert/Data/NCEP/new-tar', '/tmp/ncep-working-dir', '/tmp/ncep-untar')
    process_ncep_tars('/drives/d/UserData', '/tmp/ncep-working-dir', '/tmp/ncep-untar')
