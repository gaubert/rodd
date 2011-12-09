'''
Created on Nov 2, 2011

@author: guillaume.aubert@eumetsat.int
'''
import re
import os
import datetime
import eumetsat.dmon.common.time_utils as common_time

# potential gems header that is added (dirmon.log: Entry detected: or send.log:  Entry detected: or recv.log:  Entry detected:)
# needs to be eaten by the regular expression
TELLICASTLOG_GEMS_HEADER  = r'\s*(send.log:|dirmon.log:|recv.log:)?.*'

TELLICASTLOG_LVL          = r'(?P<lvl>(ERR|MSG|VRB|WRN))'
TELLICASTLOG_DATE         = r'(?P<datetime>(?P<date>(?P<year>(18|19|[2-5][0-9])\d\d)[-/.](?P<month>(0[1-9]|1[012]|[1-9]))[-/.](?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])))([tT ]?(?P<time>([0-1][0-9]|2[0-3]|[0-9])([:]?([0-5][0-9]|[0-9]))?([:]([0-5][0-9]|[0-9]))?([.]([0-9])+)?))?)'
TELLICASTLOG_MSG          = r'(?P<msg>.*)'

TELLICASTLOG_PATTERN      = TELLICASTLOG_GEMS_HEADER + TELLICASTLOG_LVL + r':' + TELLICASTLOG_DATE + r':' + TELLICASTLOG_MSG

TELLICASTLOG_HEADER_PATTERN = r'Lvl:Date[ ]*Time[ ]*\(UTC\)[ ]*:Message'

TELLICASTLOG_RE           = re.compile(TELLICASTLOG_PATTERN)
TELLICASTLOG_HEADER_RE    = re.compile(TELLICASTLOG_HEADER_PATTERN)



#DIRMON PATTERNS for the different dirmon events
DIRMON_ADDING_MSG_PATTERN = r'Adding file \'(?P<file>.*)\' to job \'(?P<job>.*)\', last modified: .*, size: (?P<size>\d+)'
DIRMON_MSG_ADDING_RE      = re.compile(DIRMON_ADDING_MSG_PATTERN)

DIRMON_JOB_ACTIVATED_PATTERN = r'Job activated: File "(?P<job>.*)" was successfully generated.'
DIRMON_JOB_ACTIVATED_RE      = re.compile(DIRMON_JOB_ACTIVATED_PATTERN)

DIRMON_JOB_RELEASED_PATTERN = r'Releasing resources for job "(?P<job>.*)" found in directory ".*"\.'
DIRMON_JOB_RELEASED_RE      = re.compile(DIRMON_JOB_RELEASED_PATTERN)

DIRMON_PATTERNS = { 'adding'     : DIRMON_MSG_ADDING_RE , 
                    'activating' : DIRMON_JOB_ACTIVATED_RE,
                    'releasing'  : DIRMON_JOB_RELEASED_RE,
                  }

# tc-send patterns
TCSEND_CHAN_ANNOUNCED    = r'Channel "(?P<channel>.*)" announced'
TCSEND_CHAN_ANNOUNCED_RE = re.compile(TCSEND_CHAN_ANNOUNCED)

TCSEND_JOB_ANNOUNCED     = r'Content for job "(?P<job>.*)" on channel "(?P<channel>.*)" is announced\.'
TCSEND_JOB_ANNOUNCED_RE  = re.compile(TCSEND_JOB_ANNOUNCED)

TCSEND_JOB_ACTIVATED     = r'Job "(?P<job>.*)" on channel "(?P<channel>.*)" activated\.'
TCSEND_JOB_ACTIVATED_RE  = re.compile(TCSEND_JOB_ACTIVATED)

TCSEND_JOB_BLOCKED     = r'Job "(?P<job>.*)" blocked: Waiting for channel "(?P<channel>.*)"'
TCSEND_JOB_BLOCKED_RE  = re.compile(TCSEND_JOB_BLOCKED)

TCSEND_JOB_ABORTED      = r'FileBroadcast job "(?P<job>.*)" on channel "(?P<channel>.*)" aborted.' 
TCSEND_JOB_ABORTED_RE   = re.compile(TCSEND_JOB_ABORTED)

TCSEND_JOB_FINISHED      = r'FileBroadcast job "(?P<job>.*)" on channel "(?P<channel>.*)" done'
TCSEND_JOB_FINISHED_RE   = re.compile(TCSEND_JOB_FINISHED)

TCSEND_CHAN_CLOSED      = r'Closing channel "(?P<channel>.*)"\.'
TCSEND_CHAN_CLOSED_RE   = re.compile(TCSEND_CHAN_CLOSED)

TCSEND_PATTERNS = {
                    'chan_announced'  : TCSEND_CHAN_ANNOUNCED_RE,
                    'job_announced'   : TCSEND_JOB_ANNOUNCED_RE,
                    'job_activated'   : TCSEND_JOB_ACTIVATED_RE,
                    'job_blocked'     : TCSEND_JOB_BLOCKED_RE,
                    'job_aborted'     : TCSEND_JOB_ABORTED_RE,
                    'job_finished'    : TCSEND_JOB_FINISHED_RE,
                    'chan_closed'     : TCSEND_CHAN_CLOSED_RE,
                  }

#tc-recv patterns
#Received announcement for channel `MFREURG16', address 224.223.222.116:2116 (subscribed)
TCRECV_ANNOUNCEMENT     = r'Received announcement for channel [`|\'](?P<channel>.*)[`|\'], address .* \(subscribed\)'
TCRECV_ANNOUNCEMENT_RE  = re.compile(TCRECV_ANNOUNCEMENT)

TCRECV_CONNECTING       = r'Connecting to data channel [`|\'](?P<channel>.*)[`|\'], address \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,6} \(invited\)'
TCRECV_CONNECTING_RE    = re.compile(TCRECV_CONNECTING)

TCRECV_CONNECTED        = r'Connected to data channel [`|\'](?P<channel>.*)[`|\'], address \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,6} \(invited\)'
TCRECV_CONNECTED_RE     = re.compile(TCRECV_CONNECTED)

TCRECV_RECEIVED         = r'Received file .* on channel [`|\'](?P<channel>.*)[`|\']'
TCRECV_RECEIVED_RE      = re.compile(TCRECV_RECEIVED)

TCRECV_DELIVERED         = r'Delivered file [`|\'](?P<file>.*)[`|\'] id (?P<id>.*) from channel [`|\'](?P<channel>.*)[`|\']'
TCRECV_DELIVERED_RE      = re.compile(TCRECV_DELIVERED)

TCRECV_DELIVERED_ALL     = r'Delivered all \d{1,5} files of filelist (?P<id>.*) from channel [`|\'](?P<channel>.*)[`|\']'
TCRECV_DELIVERED_ALL_RE  = re.compile(TCRECV_DELIVERED_ALL)

TCRECV_DISCONNECTED      = r'Disconnect from data channel [`|\'](?P<channel>.*)[`|\'], address \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,6} completed \(finished\)'
TCRECV_DISCONNECTED_RE   = re.compile(TCRECV_DISCONNECTED)

TCRECV_PATTERNS = {
                    'announcement' :  TCRECV_ANNOUNCEMENT_RE,
                    'connecting'   :  TCRECV_CONNECTING_RE,
                    'connected'    :   TCRECV_CONNECTED_RE,
                    'received_file':  TCRECV_RECEIVED_RE,
                    'delivered'    :  TCRECV_DELIVERED_RE,
                    'delivered_all':  TCRECV_DELIVERED_ALL_RE,
                    'disconnected' :  TCRECV_DISCONNECTED_RE,
                  }

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

    def __init__(self, a_app_type='dirmon'):
        '''
        constructor
        '''
        self._gen        = None
        self._lines      = None
        self._app_type   = a_app_type
        
    def set_lines_to_parse(self, a_lines=None):
        """
           Set an iterable
        """
        if a_lines:
            self._lines = a_lines
            self._gen   = self._create_parser_gen()
    
    def parse_one_line(self, a_line):
        """
           Parse one unique line
        """
        result = self._parse_line(a_line) 
            
        if result:
            if self._app_type == "dirmon":
                extra_result = self._parse_dirmon_msg(result['msg'])
                result.update(extra_result)
            elif self._app_type == "tc-send":
                extra_result = self._parse_tcsend_msg(result['msg'])
                result.update(extra_result)
            elif self._app_type == "tc-recv":
                extra_result = self._parse_tcrecv_msg(result['msg'])
                result.update(extra_result)
        else:
            #for the moment raise an exception
            raise InvalidTellicastlogFormatError("Tellicastlog parser: Unkown line format %s" %(a_line))
        
        return result
            
  
    def _create_parser_gen(self):
        """
          Create the parser generator
        """
        for line in self._lines:
                    
            result = self._parse_line(line) 
            
            if result:
                if self._app_type == "dirmon":
                    extra_result = self._parse_dirmon_msg(result['msg'])
                    result.update(extra_result)
                elif self._app_type == "tc-send":
                    extra_result = self._parse_tcsend_msg(result['msg'])
                    result.update(extra_result)
                elif self._app_type == "tc-recv":
                    extra_result = self._parse_tcrecv_msg(result['msg'])
                    result.update(extra_result)
                
                yield result
                
    def _parse_tcrecv_msg(self, a_msg):
        """
           Parse tcrecv msg
        """
        for (key, val) in TCRECV_PATTERNS.iteritems():
            matched = val.match(a_msg)
            if matched:
                if key == "announcement":
                    return { "channel"     : matched.group('channel'),
                             "chan_status" : "announcement", 
                           }
                elif key == "connecting":
                    return { "channel"      : matched.group('channel'),
                             "chan_status"  : "connecting", 
                           }
                elif key == "connected":
                    return { "channel"      : matched.group('channel'),
                             "chan_status"  : "connected", 
                           }
                elif key == "received_file":
                    return { "channel"     : matched.group('channel'),
                             "chan_status" : "received_file", 
                           }
                    #file delivered
                elif key == "delivered":
                    return { "file"       : matched.group('file'),
                             "channel"    : matched.group('channel'),
                             "file_id"    : matched.group('id'),
                             "chan_status" : "delivered_file", 
                           }
                elif key == "delivered_all":
                    return { "channel"     : matched.group('channel'),
                              "filelist"   : matched.group('id'),
                             "chan_status" : "delivered_all", 
                           }
                elif key == "disconnected":
                    return { "channel"     : matched.group('channel'),
                             "chan_status" : "disconnected", 
                           }
                else:
                    #security against bugs
                    return {}
        
        return {}
    
    def _clean_jobname(self, a_job):
        """
           Clean jobname (remove path artifacts, job suffix, ...)
        """
        job = os.path.basename(a_job)
        pos = job.rfind('.')
        return job[:pos] if pos != -1 else job
    
    def _clean_filename(self, filename):
        """
           split directories from basename
           return (dir, basename)
        """
        return os.path.split(filename)
        
                
    def _parse_dirmon_msg(self, a_msg):
        """
           Parse dirmon msg
        """
        for (key, val) in DIRMON_PATTERNS.iteritems():
            matched = val.match(a_msg)
            if matched:
                if key == "adding":
                    dir_name, the_basename = self._clean_filename(matched.group('file'))
                    return { "file" : the_basename,
                             "metadata"  : { 'dirmon_dir' : os.path.basename(dir_name) },
                             "job"  : self._clean_jobname(matched.group('job')),
                             "job_status" : "created", 
                           }
                elif key == "activating":
                    
                    #clean the job name as it is the file here
                    
                    return { "job"  : self._clean_jobname(matched.group('job')),
                             "job_status" : "activated", 
                           }
                elif key == "releasing":
                    return {
                             "job" :  self._clean_jobname(matched.group('job')),
                             "job_status" : "released", 
                           }
                else:
                    #security against bugs
                    return {}
        
        return {}
    
    def _parse_tcsend_msg(self, a_msg):
        """
           Parse tcsend msg
        """
        for (key, val) in TCSEND_PATTERNS.iteritems():
            matched = val.match(a_msg)
            if matched:
                if key == "chan_announced":
                    return { "channel" : matched.group('channel'),
                             "chan_status" : "announced", 
                           }
                elif key == "job_announced":
                    
                    return { "job"  : self._clean_jobname(matched.group('job')),
                             "channel"    : matched.group('channel'),
                             "job_status" : "announced", 
                           }
                elif key == "job_activated":
                    return { "job"  : self._clean_jobname(matched.group('job')),
                             "channel"    : matched.group('channel'),
                             "job_status" : "activated", 
                           }
                elif key == "job_blocked":
                    return { "job"  : self._clean_jobname(matched.group('job')),
                             "channel"    : matched.group('channel'),
                             "job_status" : "blocked", 
                           }
                elif key == "job_aborted":
                    return { "job"  : self._clean_jobname(matched.group('job')),
                             "channel"    : matched.group('channel'),
                             "job_status" : "aborted", 
                           }
                elif key == "job_finished":
                    return { "job"  : self._clean_jobname(matched.group('job')),
                             "channel"    : matched.group('channel'),
                             "job_status" : "finished", 
                           }
                elif key == "chan_closed":
                    return { "channel" : matched.group('channel'),
                             "chan_status" : "closed", 
                           }
                else:
                    #security against bugs
                    return {}
        
        return {}
    
    def __iter__(self):
        """ 
            iterator from the begining of the stream.
            If you call twice this method the second iterator will continue to iterate from 
            where the previous one was and it will not create a new one.
            To create a you one, you have to pass the io_prog again. 
        """
        if not self._gen:
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
            
    def _tellicastdatetime_to_datetime(self, a_date_str, a_year, a_month, a_day, a_time): #pylint: disable-msg=R0913
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
                the_time = a_time[:pos]
                the_microsec = int(float(a_time[pos:])*1e6)
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
                raise InvalidDateError("The time part of the date %s is not following the Tellicast date format"  % (a_date_str))
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
                    'app' : self._app_type,
                    'time': self._tellicastdatetime_to_datetime(matched.group('datetime'), \
                                                                matched.group('year'), \
                                                                matched.group('month'), \
                                                                matched.group('day'), \
                                                                matched.group('time')),
                    'lvl' : matched.group('lvl'),
                    'msg' : matched.group('msg'),
                    #'full_msg' : a_line,
                    
                   }
        else:
            #try to eat the potential header
            header_matched = TELLICASTLOG_HEADER_RE.match(a_line)
            
            if not header_matched:
                raise InvalidTellicastlogFormatError("Invalid Tellicast log format for [%s]\n" %(a_line))
           
            return
        
if __name__ == '__main__':
    
    sendlog_test_path  = '/homespace/gaubert/logs/tests/send_test.log'
    sendlog_path       = '/homespace/gaubert/logs/tests/send.log'
    sendlog_path1      = '/homespace/gaubert/logs/tests/send.log.1'
    sendlog_path2      = '/homespace/gaubert/logs/tests/send.log.2'
    
    dirmonlog_path       = '/homespace/gaubert/logs/tests/dirmon.log'
    dirmonlog_path1      = '/homespace/gaubert/logs/tests/dirmon.log.1'
    dirmonlog_path2      = '/homespace/gaubert/logs/tests/dirmon.log.2'
    
    recvlog_path         = '/homespace/gaubert/logs/tests/recv.log'
    
    
    s_parser = TellicastLogParser('tc-send')
    d_parser = TellicastLogParser('dirmon')
    r_parser = TellicastLogParser('tc-recv')
    
    #files = [open(sendlog_path), open(sendlog_path1), open(sendlog_path2)]
    #files = [oa_linespen(sendlog_test_path)]
    send_files   = [open(sendlog_path), open(sendlog_path1)]
    dirmon_files = [open(dirmonlog_path), open(dirmonlog_path1)]
    recv_files   = [open(recvlog_path)]
    
    tokens = { 'dirmon' : [],
               'tc-send' : []}
    
    the_file = ['send.log: Entry detected: MSG:2011-11-30 12:41:42.091:FileBroadcast job "retim-4010-53359-2011-11-30-12-41-04-203.job" on channel "MFRAFRG2" done.']
    
    result = d_parser.parse_one_line("VRB:2011-12-01 09:30:34.307:Adding file '/home/eumetsat/data/dwd/groups/DWD-DWDintern/gts01-VHDL30_DWSG_010800-1112010930-afsv--25-ia5' to job 'DWD-DWDintern-58556-2011-12-01-09-30-34-295', last modified: 2011-12-01 09:30:07, size: 1581")
    print(result)
    dirmon_dir = result['metadata']['dirmon_dir']
    #special case for DWD (should hopefully disappear in the future
    if dirmon_dir == 'wmo-ra6' or dirmon_dir.startswith('DWD'):
        print("DWD")
    import sys
    sys.exit(1)
    
    result = s_parser.parse_one_line('send.log: Entry detected: MSG:2011-11-30 12:41:42.091:FileBroadcast job "retim-4010-53359-2011-11-30-12-41-04-203.job" on channel "MFRAFRG2" done.')
    print(result)
        
       
        