'''
Created on Nov 2, 2011

@author: guillaume.aubert@eumetsat.int
'''
import re
import datetime
import time_utils as common_time


TELLICASTLOG_LVL          = r'(?P<lvl>(ERR||MSG|VRB|WRN))'
TELLICASTLOG_DATE         = r'(?P<datetime>(?P<date>(?P<year>(18|19|[2-5][0-9])\d\d)[-/.](?P<month>(0[1-9]|1[012]|[1-9]))[-/.](?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])))([tT ]?(?P<time>([0-1][0-9]|2[0-3]|[0-9])([:]?([0-5][0-9]|[0-9]))?([:]([0-5][0-9]|[0-9]))?([.]([0-9])+)?))?)'
TELLICASTLOG_MSG          = r'(?P<msg>.*)'
#r'(?P<date> (?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dev) (?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])) (?P<time>([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])) )'
TELLICASTLOG_PATTERN      = TELLICASTLOG_LVL + r':' + TELLICASTLOG_DATE + r':' + TELLICASTLOG_MSG

TELLICASTLOG_HEADER_PATTERN = r'Lvl:Date[ ]*Time[ ]*\(UTC\)[ ]*:Message'

TELLICASTLOG_RE           = re.compile(TELLICASTLOG_PATTERN)
TELLICASTLOG_HEADER_RE    = re.compile(TELLICASTLOG_HEADER_PATTERN)

class InvalidTellicastlogFormatError(Exception):
    """ Invalid IMS Date Error exception """
    def __init__(self, a_msg):
        super(InvalidTellicastlogFormatError, self).__init__(a_msg)

class InvalidDateError(Exception):
    """ Invalid Date Error exception """
    def __init__(self, a_msg):
        super(InvalidDateError, self).__init__(a_msg)

class TellicastLogParser(object):
    '''
    TellicastLogParser
    '''

    def __init__(self):
        '''
        constructor
        '''
        self._gen   = None
        self._lines = None
        
    def set_lines_to_parse(self, a_lines=None):
        """
           Set an iterable
        """
        if a_lines:
            self._lines = a_lines
        
        #self._gen = self._create_parser_gen()
        
        
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
            
    def _tellicastdatetime_to_datetime(self, a_date_str, a_year, a_month, a_day, a_time):
        """ Return datetime from the tellicast dates
            
            Args: a_date_str : a tellicast formatted date string
                  a_year: the year
                  a_month: the month
                  a_day: the day
                  a_time: the time
                   
            Returns: a DateTime Object
            
            Raises:
                exception InvalidTellicastLogFormatError if this is an unvalid date
        """     
        the_year   = int(a_year)
        the_month  = int(a_month)
        the_day    = int(a_day)
            
        if a_time:
            the_microsec = 0
            
            # if we have milliseconds
            pos = a_time.find('.')
            if pos >= 0:
                fracsec = a_time[pos:]
                the_time = a_time[:pos]
                the_microsec = int(float(fracsec)*1e6)
            else:
                the_microsec = 0
                
            time_list = the_time.split(":")
            if len(time_list) == 1:
                # there is only one value and according the reg expr it has to be an hour
                the_h   = int(time_list[0])
                the_min = 0
                the_sec = 0
            elif len(time_list) == 2:
                #min and hours 
                the_h   = int(time_list[0])
                the_min = int(time_list[1])
                the_sec = 0
            elif len(time_list) == 3:
                #min and hours 
                the_h   = int(time_list[0])
                the_min = int(time_list[1])
                the_sec = int(time_list[2])
            else:
                raise InvalidDateError("The time part of the date %s is not following the Tellicast date format" %(a_date_str))
        else:
            the_h        = 0
            the_min      = 0
            the_sec      = 0
            the_microsec = 0
              
        return datetime.datetime(the_year, the_month, the_day,  the_h, the_min, the_sec, the_microsec, tzinfo = common_time.UTC_TZ)
   
       
    def _parse_line(self, a_line):
        """ 
          parse the line
        """
        
        #print("line = %s" %(a_line))
        matched = TELLICASTLOG_RE.match(a_line)
    
        
        if matched:
            return {
                    'app' : 'tc-send',
                    'time': self._tellicastdatetime_to_datetime(matched.group('datetime'), \
                                                                matched.group('year'), \
                                                                matched.group('month'), \
                                                                matched.group('day'), \
                                                                matched.group('time')),
                    'lev' : matched.group('lvl'),
                    'msg' : matched.group('msg'),
                    'full_msg' : a_line,
                    
                   }
        else:
            header_matched = TELLICASTLOG_HEADER_RE.match(a_line)
            
            if not header_matched:
                raise InvalidTellicastlogFormatError("Invalid Tellicast log format for %s\n" %(a_line))
           
            return
        
if __name__ == '__main__':
    
    sendlog_test_path  = '/homespace/gaubert/logs/tests/send_test.log'
    sendlog_path       = '/homespace/gaubert/logs/tests/send.log'
    sendlog_path1      = '/homespace/gaubert/logs/tests/send.log.1'
    sendlog_path2      = '/homespace/gaubert/logs/tests/send.log.2'
    
    dirmonlog_path       = '/homespace/gaubert/logs/tests/dirmon.log'
    dirmonlog_path1      = '/homespace/gaubert/logs/tests/dirmon.log.1'
    dirmonlog_path2      = '/homespace/gaubert/logs/tests/dirmon.log.2'
    
    
    parser = TellicastLogParser()
    
    #files = [open(sendlog_path), open(sendlog_path1), open(sendlog_path2)]
    files = [open(sendlog_test_path)]
    #files = [open(dirmonlog_path)]
    
    for file in files: 
        print("FILE START **********************************************\n\n\n")
        parser.set_lines_to_parse(file)
        
        for token in parser:
            print(token)
        
       
        