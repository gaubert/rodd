'''
Created on Oct 27, 2011

@author: guillaume.aubert@eumetsat.int
'''
import re
import datetime

#regular Expression to parse the xferlogs
XFERLOG_DATE_PATTERN = r'(?P<date>(?P<wday>Mon|Tue|Wed|Thu|Fri|Sat|Sun) (?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dev) (?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])) (?P<time>([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])) (?P<year>(18|19|[2-5][0-9])\d\d))'
XFERLOG_TRANSFERTIME = r'(?P<transfer_time>\d+)'
XFERLOG_HOST         = r'(?P<host>\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)'
XFERLOG_FILESIZE     = r'(?P<filesize>\S+)'
XFERLOG_FILENAME     = r'(?P<filename>\S+)'
XFERLOG_REST         = r'(?P<transfer_type>\S+) (?P<special_action_flag>\S+) (?P<direction>\S+) (?P<access_mode>\S+) (?P<username>\S+) (?P<service_name>\S+) (?P<authentication_method>\S+) (?P<authenticated_user_id>\S+) (?P<completion_status>\S+)'

XFERLOG_PATTERN      = XFERLOG_DATE_PATTERN + r' ' + XFERLOG_TRANSFERTIME + r' ' + XFERLOG_HOST + r' ' + XFERLOG_FILESIZE + r' ' + XFERLOG_FILENAME + r' ' + XFERLOG_REST

XFERLOG_RE           = re.compile(XFERLOG_PATTERN)


class InvalidXferlogFormatError(Exception):
    """ Invalid IMS Date Error exception """
    def __init__(self, a_msg):
        super(InvalidXferlogFormatError, self).__init__(a_msg)

class XferlogIndexer(object):
    '''
    Receive an xferlog line and create a json document following a predefined structure
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    
    def read(self, a_lines):
        '''
           read a set of xferlog lines and create a json structure for each of them
        '''
        
        for line in a_lines:
            print(self._parse_line(line))
            
    def _convert_date_to_date_time(self, a_date):
        """
           xferlog date to datetime
        """
        return datetime.datetime.strptime(a_date, '%a %b %d %H:%M:%S %Y')
    
    def _remove_tmp(self, filename):
        """
          remove tmp in the filename if there is one
        """
        if filename[-4:] == '.tmp':
            return filename[:-4]
        else:
            return filename
            
    
    def _parse_line(self, a_line):
        """ 
          parse the line
        """
        
        matched = XFERLOG_RE.match(a_line)
        
        if matched:
            return {
                       'app' : 'proftpd',
                       'time': self._convert_date_to_date_time(matched.group('date')),
                       'lev' : 'info',
                       'full_msg' : a_line,
                       'file' : self._remove_tmp(matched.group('filename')),
                       'file_size' : matched.group('filesize'),
                       'transfer_time' : matched.group('transfer_time'),
                       
                     } 
        else:
            raise InvalidXferlogFormatError("Invalid xferlog format for %s\n" %(a_line))
            

if __name__ == '__main__':
    
    xferlog_test_path  = '/homespace/gaubert/logs/tests/xferlog_test'
    xferlog_path  = '/homespace/gaubert/logs/tests/xferlog'
    xferlog_path1 = '/homespace/gaubert/logs/tests/xferlog'
    xferlog_path2 = '/homespace/gaubert/logs/tests/xferlog'
    
    
    indexer = XferlogIndexer()
    
    files = [open(xferlog_path), open(xferlog_path1), open(xferlog_path2)]
    files = [open(xferlog_test_path)]
    
    for file in files: 
       print("FILE START **********************************************\n\n\n")
       indexer.read(file)