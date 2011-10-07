'''
Created on 7 Oct 2011

@author: guillaume.aubert@eumetsat.int
'''
import string
import datetime
import os

def get_datetime_from_ISO8601(aISOStr):
    """ transform a ISO 8601 string into a Datetime """

    # if there is a no T, there is no time component add it T00:00:00 to the date
    if not aISOStr.find('T'):
        the_str = '%sT00:00:00'
    else:
        the_str = aISOStr
    
    return datetime.datetime.strptime(the_str,'%Y-%m-%dT%H:%M:%S')

def get_datetime_from_GEMSDate(a_str):
    """ transform a GEMS Date string into a Datetime """
    
    return datetime.datetime.strptime(a_str,'%Y-%m-%d %H:%M:%S')

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
    
    def __init__(self, send_file):
        """ constructor """
        
        self.send_file = send_file
        self.reader    = BackwardsReader(send_file)
        self.dt        = None
        
        self._read_latest_announcement_date()
        
    
    def _read_latest_announcement_date(self):
        """ read the latest time there was an announcement """
        
        if os.path.exists(AnnouncementMonitor.LATEST_ANN_PATH):
            ann_file = open(AnnouncementMonitor.LATEST_ANN_PATH)
        
            # read first line
            line = ann_file.readline()
            
            self.dt = get_datetime_from_ISO8601(line.strip())
        
    def check(self):
        """ check that announcement is ok """
        continue_reading = True
        cpt = 0
        
        str_to_find = "announced"
        
        while continue_reading:
            line = self.reader.readline()
            found = line.find(str_to_find) 
            if found != -1:
                # do not parse the date but stupidely take a substring
                the_date = line[4:23]
                print("announcement working:[%s]\n" %(the_date))
                latest_ann_date = get_datetime_from_GEMSDate(the_date)
                
                self.check_condition(latest_ann_date, self.dt)
                
            cpt += 1
            if cpt == 30:
                break 
            
    def check_condition(self, latest, previous):
        """ 
            Check that the time between the latest announcement and
            the previous one are no less than TIME_BET_ANN      
        """
        
        if previous:
            delta = latest - previous
            
            print("delta in seconds = %d\n" % (delta.seconds))
        
        

if __name__ == '__main__':
    
    monitor = AnnouncementMonitor("./send.log")
    
    monitor.check()
    
   
    
