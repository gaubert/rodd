'''
Created on Oct 27, 2011

@author: guillaume.aubert@eumetsat.int
'''
import re
import os
import datetime

#regular Expression to parse the xferlogs
#to eat potential header addded by GEMS
XFERLOG_GEMS_HEADER  = r'\s*(xferlog:)?.*'
XFERLOG_DATE_PATTERN = r'(?P<date>(?P<wday>Mon|Tue|Wed|Thu|Fri|Sat|Sun) (?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dev) (?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])) (?P<time>([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])) (?P<year>(18|19|[2-5][0-9])\d\d))'
XFERLOG_TRANSFERTIME = r'(?P<transfer_time>\d+)'
XFERLOG_HOST         = r'(?P<host>(::ffff:)?\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)'
XFERLOG_FILESIZE     = r'(?P<filesize>\S+)'
XFERLOG_FILENAME     = r'(?P<filename>\S+)'
XFERLOG_REST         = r'(?P<transfer_type>\S+) (?P<special_action_flag>\S+) (?P<direction>\S+) (?P<access_mode>\S+) (?P<username>\S+) (?P<service_name>\S+) (?P<authentication_method>\S+) (?P<authenticated_user_id>\S+) (?P<completion_status>\S+)'

XFERLOG_PATTERN      =  XFERLOG_GEMS_HEADER + \
                        XFERLOG_DATE_PATTERN + r' ' +\
                        XFERLOG_TRANSFERTIME + r' ' + \
                        XFERLOG_HOST + r' ' +\
                        XFERLOG_FILESIZE + r' ' +\
                        XFERLOG_FILENAME + r' ' +\
                        XFERLOG_REST

XFERLOG_RE           = re.compile(XFERLOG_PATTERN)


class InvalidXferlogFormatError(Exception):
    """ Invalid IMS Date Error exception """
    def __init__(self, a_msg):
        super(InvalidXferlogFormatError, self).__init__(a_msg)

class XferlogParser(object):
    '''
    Receive an xferlog line and create a json document following a predefined structure
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._gen   = None
        self._lines = None
        
    def set_lines_to_parse(self, a_lines=None):
        """
           Set an iterable
        """
        if a_lines:
            self._lines = a_lines
        
    def _create_parser_gen(self):
        """
          Create the parser generator
        """
        for line in self._lines:
            result = self._parse_line(line) 
            if result:
                yield result
    
    def __iter__(self):
        """ 
            iterator from the begining of the stream.
            If you call twice this method the second iterator will continue to iterate from 
            where the previous one was and it will not create a new one.
            To create a you one, you have to pass the io_prog again. 
        """
        self._gen = self._create_parser_gen()
        
        return self
    
    def next(self):
        """
           Return the next token
            
           Returns:
               return next found token 
        """
        
        # if no generator have been created first do it and call next
        if self._gen == None:
            self._gen = self._create_parser_gen()
        
        return self._gen.next() #pylint: disable-msg=E1103
    
    def read(self, a_lines):
        '''
           read a set of xferlog lines and create a json structure for each of them
           a_lines: An iterable containing lines
        '''
        
        for line in a_lines:
            print(self._parse_line(line))
    
    def parse_one_line(self, a_line):
        """
           Parse a unique line
        """
        return self._parse_line(a_line)
            
    def _convert_date_to_date_time(self, a_date):
        """
           xferlog date to datetime
        """
        return datetime.datetime.strptime(a_date, '%a %b %d %H:%M:%S %Y')
    
    def _clean_dwd_filename(self,filename):
        """
           remove dwd prefix
           If it is a DWD file name remove the prefix (ninjo_, ra6_)
        """
        if filename.startswith('ninjo_') or filename.startswith('ra6_'):
            return filename[filename.find("_")+1:]
        else:
            return filename
    
    def _clean_filename(self, filename):
        """
          remove tmp in the filename if there is one
        """
        
        #get basename remove dir (dir could be kept as it is a relevant info)
        dir_name, the_basename = os.path.split(filename)
        
        the_basename = self._clean_dwd_filename(the_basename)
        
        #remove suffix
        name, ext = os.path.splitext(the_basename)
        
        if ext.lower() in ['.tmp','.temp']:
            return (dir_name, name)
        else:
            return (dir_name, the_basename)
            
    def _parse_line(self, a_line):
        """ 
          parse the line
        """
        
        matched = XFERLOG_RE.match(a_line)
        
        if matched:
            
            the_dir, the_filename = self._clean_filename(matched.group('filename'))
            
            return {
                       'app' : 'proftpd',
                       'time': self._convert_date_to_date_time(matched.group('date')),
                       'lev' : 'info',
                       'file': the_filename,
                       'dir' : the_dir, 
                       'file_size' : matched.group('filesize'),
                       'transfer_time' : matched.group('transfer_time'),
                       #'full_msg' : a_line,
                       
                     } 
        else:
            raise InvalidXferlogFormatError("Invalid xferlog format for %s\n" %(a_line))
            

if __name__ == '__main__':
    
    xferlog_test_path  = '/homespace/gaubert/logs/tests/xferlog_test'
    xferlog_path       = '/homespace/gaubert/logs/tests/xferlog'
    xferlog_path1      = '/homespace/gaubert/logs/tests/xferlog'
    xferlog_path2      = '/homespace/gaubert/logs/tests/xferlog'
    
    
    parser = XferlogParser()
    
    files = [open(xferlog_path), open(xferlog_path1), open(xferlog_path2)]
    files = [open(xferlog_test_path)]
    
    for file in files: 
        print("FILE START **********************************************\n\n\n")
        parser.set_lines_to_parse(file)
        for token in parser:
            print(token)