#!/usr/bin/python

'''
Created on 10 Oct 2011

@author: guillaume.aubert@eumetsat.int
'''
import string
import datetime
import time
import os
import sys

def get_local_time_as_str():
    """ get local time as string """
    return time.strftime('%Y-%m-%d %H:%M:%S')

def get_datetime_from_GEMSDate(a_str):
    """ transform a GEMS Date string into a Datetime """
    
    if hasattr(datetime, 'strptime'):
        #python 2.6
        strptime = datetime.datetime.strptime
    else:
        #python 2.4 equivalent
        strptime = lambda date_string, format: datetime.datetime(*(time.strptime(date_string, format)[0:6]))
    
    return strptime(a_str,'%Y-%m-%d %H:%M:%S')

class BackwardsReader:
    
  def __init__(self, file, blksize=4096):
    """initialize the internal structures"""
    # get the file size
    self.size = os.stat(file)[6]
    # how big of a block to read from the file...
    self.blksize = blksize
    # how many blocks we've read
    self.blkcount = 1
    self.f = open(file, 'rb')
    # if the file is smaller than the blocksize, read a block,
    # otherwise, read the whole thing...
    if self.size > self.blksize:
      self.f.seek(-self.blksize * self.blkcount, 2) # read from end of file
    self.data = string.split(self.f.read(self.blksize), '\n')
    # strip the last item if it's empty...  a byproduct of the last line having
    # a newline at the end of it
    if not self.data[-1]:
        # self.data.pop()
        self.data = self.data[:-1]
      
  def readline(self):
    """ readline """
    while len(self.data) == 1 and ((self.blkcount * self.blksize) < self.size):
        self.blkcount = self.blkcount + 1
        line = self.data[0]
        try:
            self.f.seek(-self.blksize * self.blkcount, 2) # read from end of file
            self.data = string.split(self.f.read(self.blksize) + line, '\n')
        except IOError:  # can't seek before the beginning of the file
            self.f.seek(0)
            self.data = string.split(self.f.read(self.size - (self.blksize * (self.blkcount-1))) + line, '\n')
        
    if len(self.data) == 0:
        return ""

    # self.data.pop()
    # make it compatible with python <= 1.5.1
    line = self.data[-1]
    self.data = self.data[:-1]
    return line + '\n'
      
      
class AnnouncementMonitor:
    
    LATEST_ANN_PATH = ".latest_announcement"
    TIME_BET_ANN    = 300
    
    def __init__(self, send_file_dir):
        """ constructor """
        
        self.send_file_dir = send_file_dir
        
    def check(self): 
        """ check """     
        
        send_log  = "%s/send.log" % (self.send_file_dir)
        
        send_log1 = "%s/send.log.1" % (self.send_file_dir)
        
        if not os.path.exists(send_log):
            print >> sys.stderr, "WRN: %s is not present. Do nothing" % (send_log)
            return
            
        # look into send.log
        print("INF: Look into %s\n" % (send_log))
        self.check_file(send_log)
        
        # look into send.log.1 as it has the anouncement not been found
        print("INF: Look into %s\n" % (send_log1))
        self.check_file(send_log1)
        
        print >> sys.stderr, "WRN: Very Stange could not find any announcement in send.log and send.log.1. Do Nothing"
        
    def check_file(self, file_to_read):
        """ check that announcement is ok in given file """
        
        #print("Check in to %s\n" % (file_to_read))
        
        reader      = BackwardsReader(file_to_read)
        str_to_find = "announced"
        
        while True:
            line = reader.readline()
            #print("line = %s\n" %(line))
            
            if line:
                found = line.find(str_to_find) 
                if found != -1:
                    # do not parse the date but stupidely take a substring
                    the_date = line[4:23]
                    print("INF: latest announcement:[%s]\n" %(the_date))
                    latest_ann_date = get_datetime_from_GEMSDate(the_date)
                    
                    # problem, condition reached no announcment since last 3 minutes 
                    if self.check_condition_reached(latest_ann_date):
                        # exit on error
                        print >> sys.stderr , "ERR: Trigger Alarm"
                        sys.exit(2)
                    else:
                        print("INF: Everything is fine")
                        sys.exit(0)
            else:
                # no more lines to read
                #print("no more lines to read in %s\n" % (file_to_read))
                break
            
            
    def check_condition_reached(self, latest):
        """ Check that the latest announcement did not happen before TIME_BET_ANN secs"""
        
        current_time = datetime.datetime.now()
        
        delta = current_time - latest
        
        if delta.seconds >= AnnouncementMonitor.TIME_BET_ANN:
            print >> sys.stderr, "ERR [loc time:%s]: No announcement received for more than %s sec. Last announcement received in (h:m:s.ms) %s\n" % (get_local_time_as_str(), AnnouncementMonitor.TIME_BET_ANN, delta) 
            return True
        
        return False
        
        

if __name__ == '__main__':
    
    print("INF: ------------------------ Start checkings %s.\n" % ( datetime.datetime.now() ))
       
    monitor = AnnouncementMonitor(".")
    
    monitor.check()
     
    sys.exit(0)
    
   
    
