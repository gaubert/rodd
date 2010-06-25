r""" Return object for access the Radionuclide data locally or remotely 

"""

import logging
import os
import pwd
import subprocess

import misc
from nms_configuration.conf.conf_helper import Conf

def _complain_ifclosed(closed):
    """ internal func """
    if closed:
        raise ValueError, "I/O operation on closed file"
    
# pylint: disable-msg=R0201, R0913, R0902
    
class BaseRemoteDataSource(object):
    """ Base class for All Remote Sources
    """
    
    # Class members
    c_log = logging.getLogger("rndata.BaseRemoteDataSource")
    c_log.setLevel(logging.DEBUG)
    
    def __init__(self, a_data_path, a_id, a_remote_offset, a_remote_size):
        
        self.len = 0
        self.buflist = []
        self.pos = 0
        self.closed = False
        self.softspace = 0
        
        # my variables
         
        # get reference to the conf object
        self._conf              = Conf.get_instance()
        
        self._remote_path        = a_data_path
        
        self._id                = a_id
        
        self._local_dir          = self._conf.get("RemoteAccess", "localDir", "/tmp/cache")
        
        self._caching_activated  = self._conf.getboolean("RemoteAccess", "cachingActivated", False)
        
        self._fd                = None
        
        self._local_filename     = None
       
        # where to point in the file
        self._remote_offset      = a_remote_offset
        
        # Size to read 
        self._remote_size        = a_remote_size
        
    
    
    
    def _get_file_locally_available_in_cache(self, a_source, a_offset, a_size, a_destination): # pylint: disable-msg=C0103
        """ copy the file locally available and put it in the cache """
        
        src = open(a_source, "r")
        src.seek(a_offset)
        
        dest = open(a_destination,"w")
        
        dest.write(src.read(a_size))
        
        dest.flush()
        dest.close()
        src.close()
        
        #set self._fd once the copy has been done and return
        the_file = open(a_destination, "r")
        
        return the_file
        
    def _get_remote_file(self):
        """ abstract global data fetching method """
        raise Exception(-1,"method not implemented in Base Class. To be defined in children")

    def _get_current_user(self):
        """ get the user running the current session if the prodAccessUser isn't defined in the conf """
        
        return pwd.getpwuid(os.getuid())[0]
    

    def __iter__(self):
        return self

    def next(self):
        """A file object is its own iterator, for example iter(f) returns f
        (unless f is closed). When a file is used as an iterator, typically
        in a for loop (for example, for line in f: print line), the next()
        method is called repeatedly. This method returns the next input line,
        or raises StopIteration when EOF is hit.
        """
        _complain_ifclosed(self.closed)
        return self._fd.next()

    def close(self):
        """Free the memory buffer.
        """
        if not self.closed:
            self._fd.close()
            self.closed = True
            

    def isatty(self):
        """Returns False because StringIO objects are not connected to a
        tty-like device.
        """
        _complain_ifclosed(self.closed)
        return False

    def seek(self, pos, mode = 0):
        """Set the file's current position.

        The mode argument is optional and defaults to 0 (absolute file
        positioning); other values are 1 (seek relative to the current
        position) and 2 (seek relative to the file's end).

        There is no return value.
        """
        _complain_ifclosed(self.closed)
        self._fd.seek(pos, mode)

    def tell(self):
        """Return the file's current position."""
        _complain_ifclosed(self.closed)
        return self._fd.tell()

    def read(self, nbytes = -1):
        """Read at most size bytes from the file
        (less if the read hits EOF before obtaining size bytes).

        If the size argument is negative or omitted, read all data until EOF
        is reached. The bytes are returned as a string object. An empty
        string is returned when EOF is encountered immediately.
        """
        _complain_ifclosed(self.closed)
        return self._fd.read(nbytes)

    def readline(self, length=None):
        r"""Read one entire line from the file.

        A trailing newline character is kept in the string (but may be absent
        when a file ends with an incomplete line). If the size argument is
        present and non-negative, it is a maximum byte count (including the
        trailing newline) and an incomplete line may be returned.

        An empty string is returned only when EOF is encountered immediately.

        Note: Unlike stdio's fgets(), the returned string contains null
        characters ('\0') if they occurred in the input.
        """
        _complain_ifclosed(self.closed)
        return self._fd.readline(length)

    def readlines(self, sizehint = 0):
        """Read until EOF using readline() and return a list containing the
        lines thus read.

        If the optional sizehint argument is present, instead of reading up
        to EOF, whole lines totalling approximately sizehint bytes (or more
        to accommodate a final whole line).
        """
        return self._fd.readlines(sizehint)

    def truncate(self, size=None):
        """Truncate the file's size.

        If the optional size argument is present, the file is truncated to
        (at most) that size. The size defaults to the current position.
        The current file position is not changed unless the position
        is beyond the new file size.

        If the specified size exceeds the file's current size, the
        file remains unchanged.
        """
        _complain_ifclosed(self.closed)
        self._fd.truncate(size)

    def write(self, a_str):
        """Write a string to the file.

        There is no return value.
        """
        _complain_ifclosed(self.closed)
        self._fd.write(a_str)

    def writelines(self, iterable):
        """Write a sequence of strings to the file. The sequence can be any
        iterable object producing strings, typically a list of strings. There
        is no return value.

        (The name is intended to match readlines(); writelines() does not add
        line separators.)
        """
        self._fd.writelines(iterable)

    def flush(self):
        """Flush the internal buffer
        """
        _complain_ifclosed(self.closed)
        self._fd.flush()
        

class RemoteFSDataSource(BaseRemoteDataSource):
    """ get data from the a remote filesystem using ssh.
        fetch remote file and open a file descriptor on the local file
        and delegate all methods to the open file
    """
    
    # Class members
    c_log = logging.getLogger("rndata.RemoteFileSystemDataSource")
    c_log.setLevel(logging.DEBUG)
    
    def __init__(self, a_data_path, a_id, a_offset, a_size, a_remote_hostname=None, \
                       a_remote_script=None, a_remote_user=None):
        
        super(RemoteFSDataSource, self).__init__(a_data_path, a_id, a_offset, a_size)
        
        self._remote_script     = self._conf.get("RemoteAccess", "prodAccessScript") if a_remote_script == None else a_remote_script
        
        self._remote_hostname    = (self._conf.get("RemoteAccess", "prodAccessHost") if a_remote_hostname == None else a_remote_hostname)
        
        self._remote_user        = self._conf.get("RemoteAccess", "prodAccessUser", self._get_current_user()) if a_remote_user == None \
                                                                                                            else a_remote_user
        
        self._get_remote_file()
    
   
    def _get_remote_file(self):
        """ fetch the file and store it in a temporary location """
        
        # no local filename so use the remote file basename
        if self._local_filename is None:
            self._local_filename = os.path.basename(self._remote_path)
        
        # make local dir if not done
        misc.makedirs(self._local_dir)
            
        # path under which the file is going to be stored
        destination_path = "%s/%s" % (self._local_dir, self._local_filename)
        
        # if file there and caching activated open fd and quit
        if os.path.exists(destination_path) and self._caching_activated:
            RemoteFSDataSource.c_log.info("Fetch %s from the cache %s" % (self._remote_path, destination_path))
            self._fd = open(destination_path, "r")
            return
        # check to see if the file is not available locally
        elif os.path.exists(self._remote_path) and self._caching_activated:
            RemoteFSDataSource.c_log.info("Fetch %s" % (self._remote_path))
            self._fd = self._get_file_locally_available_in_cache(self._remote_path, self._remote_offset, \
                                                                  self._remote_size, destination_path)
        else:
            # try to get it remotely 
            # try 3 times before to fail
            tries = 1
            res   = []
        
            while tries < 4:
       
                func = subprocess.call
            
                RemoteFSDataSource.c_log.info("Trying to fetch remote file (using ssh) with\"%s %s %s %s %s %s %s\"" % \
                                              (self._remote_script, self._remote_hostname, self._remote_path, \
                                              str(self._remote_offset), str(self._remote_size), destination_path, self._remote_user))
            
                timer = misc.ftimer(func, [[self._remote_script, self._remote_hostname, self._remote_path, \
                                       str(self._remote_offset), str(self._remote_size), destination_path, self._remote_user]], \
                                       {}, res, number=1)
       
                RemoteFSDataSource.c_log.info("\nTime: %s secs \n Fetch file: %s on host: %s\n" % \
                                              (timer, self._remote_path, self._remote_hostname))
       
                if res[0] != 0:
                    if tries >= 3:
                        raise Exception(-1,"Error when executing remotely script :\"%s %s %s %s %s %s %s\". First Error code = %d\n" \
                                        % (self._remote_script, self._remote_hostname, self._remote_path, str(self._remote_offset), \
                                           str(self._remote_size), destination_path,self._remote_user,res[0]))
                    else:
                        tries += 1
                else:
                    tries += 4
              
            self._fd = open(destination_path,"r")
    
       


        

   