'''
Created on Sep 7, 2011

@author: guillaume.aubert@eumetsat.int
'''
import os
from ftplib import FTP
import json
import datetime

MAX_BLOCK_SIZE = 1024 *1024 # 1MB

class Logger(object):
    
    @classmethod
    def debug(cls, message):
        
        print("DEBUG: %s\n" % message)
        
    @classmethod
    def info(cls, message):
        
        print("INFO: %s\n" % message)
        
class FileSaverCB(object):
    """ FileSaverCallback """
    
    def __init__(self, file_path):
        """ constructor """
        
        self._file_path = file_path
        
        self.fp = open(file_path, "wb")
    
    def write(self,block):
        """ write file """
        self.fp.write(block)
    
    def close(self):
        """ close file """
        self.fp.close()
            
class TopDirList(object):
    """ TopDirList """
    def __init__(self):
        """ top dir list """
        self._list = []
    
    def add_element(self, message):
        """ add element """
        dummy = message.split()
        
        print("message %s\n" % (dummy[-1]))
        self._list.append(dummy[-1])
        
    def last(self):
        return self._list[-1]
    
    def sort(self):
        """ sort the list """
        self._list.sort(key=str.lower)
        
    def find_nearest_from(self, a_date_str):
        """ Find the nearest date in the list from the given one """
        
        min_interval= None
        max_interval= None
        
        for elem in self._list:
            if elem == a_date_str:
                min_interval  = elem
                max_interval  = elem
                #quit because we did find a match
                break
            
            elif (elem < a_date_str) and ((min_interval is None) or (elem > min_interval)):
                min_interval = elem
            elif (elem > a_date_str) and ((max_interval is None) or (elem < max_interval)):
                max_interval = elem
        
        #there are no values > to a_date_str
        if max_interval is None:
            return min_interval
        
        # with max and min now return
        if abs(int(a_date_str) - int(min_interval)) < abs(int(a_date_str) - int(max_interval)):
            return min_interval
        else:
            return max_interval
        
    # methods to make the object iterable
    def __len__(self):
        """Called to implement the built-in function len(). Should
        return the length of the object, an integer >= 0. Also, an
        object that doesn't define a __nonzero__() method and whose
        __len__() method returns zero is considered to be false in a
        Boolean context."""
        return self._list.__len__()
 
    def __getitem__(self, key):
        """Called to implement evaluation of self[key]. For sequence
        types, the accepted keys should be integers and slice objects.
        Note that the special interpretation of negative indexes (if
        the class wishes to emulate a sequence type) is up to the
        __getitem__() method. If key is of an inappropriate type,
        TypeError may be raised; if of a value outside the set of
        indexes for the sequence (after any special interpretation of
        negative values), IndexError should be raised. For mapping
        types, if key is missing (not in the container), KeyError
        should be raised. Note: for loops expect that an IndexError
        will be raised for illegal indexes to allow proper detection of
        the end of the sequence."""
        return self._list.__getitem__(key)
     
    def __setitem__(self,key,value):
        """Called to implement assignment to self[key]. Same note as
        for __getitem__(). This should only be implemented for mappings
        if the objects support changes to the values for keys, or if
        new keys can be added, or for sequences if elements can be
        replaced. The same exceptions should be raised for improper key
        values as for the __getitem__() method."""
        self._list.__setitem__(key,value)
     
    def __delitem__(self,key):
        """Called to implement deletion of self[key]. Same note as for
        __getitem__(). This should only be implemented for mappings if
        the objects support removal of keys, or for sequences if
        elements can be removed from the sequence. The same exceptions
        should be raised for improper key values as for the __getitem__
        () method."""
        self._list.__delitem__(key)
     
    # __iter__ is not strictly required, it's only needed to implement
    # efficient iteration.
    def __iter__(self):
        """This method is called when an iterator is required for a
        container. This method should return a new iterator object that
        can iterate over all the objects in the container. For
        mappings, it should iterate over the keys of the container, and
        should also be made available as the method iterkeys()."""
        return self._list.__iter__()
     
    # __contains__ isn't strictly required either, it's only needed to
    # implement the `in` operator efficiently.
    def __contains__(self,item):
        """Called to implement membership test operators. Should return
        true if item is in self, false otherwise. For mapping objects,
        this should consider the keys of the mapping rather than the
        values or the key-item pairs."""
        return self._list.__contains__(item)
     
    # Mutable sequences only, provide the Python list methods.
    def append(self,item):
        self._list.append(item)
    def count(self):
        return self._list.count()
    def index(self,item):
        return self._list.index(item)
    def extend(self,other):
        self._list.extend(other)
    def insert(self,item):
        self._list.insert(item)
    def pop(self):
        return self._list.pop()
    def remove(self,item):
        return self._list.remove(item)
    def reverse(self):
        return self._list.reverse()
    
class FileList(TopDirList):
    """ FileList keep info regarding the dictionary """
    
    def __init__(self):
        """ constructor """
        super(FileList, self).__init__()
        
        self._sizes = {}
        
    
    def add_element(self, message):
        """ add element """
        dummy = message.split()
        
        # add in list of files
        self._list.append(dummy[-1])
        
        # keep size in a dict
        self._sizes[dummy[-1]] = int(dummy[-5])
        
        print("message key=%s, val=%s\n" % (dummy[-1], self._sizes[dummy[-1]]))
        
    def get_file_size(self, filename):
        """ get_file_size """
        return self._sizes.get(filename, None)
    
        
class Synchronizer(object):
    """ synchronizer """
    
    
    def __init__(self, db_file_path, a_downloader):
        """ constructor """
        
        self._downloader   = a_downloader
                
        self._db_file_path = db_file_path
        self._db           = None
        
        self._log          = Logger
        
        
        self._load_db_file()
        
         
    def _load_db_file(self):
        """ If db exists load it otherwise create a new one """
        
        if os.path.exists(self._db_file_path):
            fp = file(self._db_file_path)
            self._db = json.load(fp)
        else:
            self._db = {}
            
    def _get_formatted_now(self):
        """ get now time formatted like on ECMWF ftp site """
        
        now = datetime.datetime.now()
        return now.strftime('%Y%m%d%H%M%S')
    
    def download_files_to_sync(self):
        """ get info from FTP server and download all the files to sync """
        
        #get list of dirs
        t_list = TopDirList()
        
        self._downloader.list(cb_func = t_list.add_element, dir = None)
        
        t_list.sort()
        
        # get latest dir treated
        latest = self._db.get('latest', t_list.last())
        
        self._downloader.cd(latest)
        
        file_list = FileList()
        
        self._downloader.list(cb_func = file_list.add_element, dir = None)
        
        dir ="/tmp/ecmwf/"
        
        nb_of_download = len(file_list)
                
        for filename in file_list:
            
            path = "%s/%s" % (dir, filename)
            
            size = file_list.get_file_size(filename)
            
            # download only if not already done
            if not (os.path.exists(path) and (os.path.getsize(path) == size) ):
                self._log.info("Downloading %s \ninto %s" %(filename, dir))
                f_cb = FileSaverCB("%s/%s" % (dir, filename))
                self._downloader.download(filename, f_cb.write)
            else:
                self._log.info("No need to download %s \n" %(filename))
            
            nb_of_download -= 1
            
            self._log.info("================ %d more files to download ================" % (nb_of_download))
            
            if (nb_of_download % 50) == 0:
                # due to some connection port issues reconnect every 100 transfers
                # reset connection
                self._log.info("======= RECONNECT ======")
                self._downloader.reconnect()
                self._downloader.cd(latest)
            

class ECMWFFtpDownloader(object):
    """ Downloader class for ECMWF Web site """
    
    def __init__(self, login, passwd, host, port=21, passive = False ):
        """ constructor """
        self._login     = login
        self._passwd    = passwd
        self._host      = host
        self._port      = port
        self._passive   = passive
        self._connected = False
        self._log       = Logger
        
    def connect(self):
        """ connect to the ftp server """
               
        self._ftp_conn = FTP()
        
        self._ftp_conn.connect(self._host, self._port)
        
        self._log.info("Connected to %s:%s" % (self._host, self._port))
        
        self._ftp_conn.login(self._login, self._passwd)
        
        # set passive mode as expected by the user
        self._ftp_conn.set_pasv(self._passive)
        
        self._connected = True
        
    def reconnect(self):
        """ reconnect to the same server """
        
        self._ftp_conn.close()
        
        self.connect()
        
    def assert_connection(self):
        """ check that it is connected """
        
        if not self._connected:
            raise Exception("Not connected to %s:%s" % (self._host, self._port))
                
    def list(self, cb_func, dir=None):
        """ list dir""" 
        
        command = 'LIST %s' %(dir) if dir else 'LIST'
        
        self._ftp_conn.retrlines(command, cb_func)
        
    def cd(self,dir):
        """ enter in dir """
        self._ftp_conn.cwd(dir)
    
    def download(self, a_filename, a_cb_func):
        """ download file using the callback function """
        
        self._ftp_conn.set_pasv(self._passive)
        
        self._ftp_conn.retrbinary("RETR %s" % (a_filename), a_cb_func, MAX_BLOCK_SIZE)

if __name__ == '__main__':
    
    downloader = ECMWFFtpDownloader('guillaume.aubert', '', 'data-portal.ecmwf.int')
    
    downloader.connect()
    
    sync = Synchronizer("/tmp/sync.db", downloader)
    
    sync.download_files_to_sync()
    
    """t_list = TopDirList()
    
    downloader.list(cb_func = t_list.add_element, dir = None)
    
    now = datetime.datetime.now()
    now_str = now.strftime('%Y%m%d%H%M%S')
    
    found = t_list.find_nearest_from('20110831000000')
    
    print("Found = %s\n" %(found))
    """
    
    
    