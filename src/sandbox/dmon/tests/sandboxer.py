'''
Created on Oct 27, 2011

@author: gaubert
'''
import re
import datetime

NLDATETIME_PATTERN  = r'(?P<date>(?P<year>(18|19|[2-5][0-9])\d\d)[-/.]?(?P<month>(0[1-9]|1[012]|[1-9]))[-/.]?(?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])))([tT ]?(?P<time>([0-1][0-9]|2[0-3]|[0-9])([:]?([0-5][0-9]|[0-9]))?([:]([0-5][0-9]|[0-9]))?([.]([0-9])+)?))?' # pylint: disable-msg=C0301
NLDATETIME_RE       = re.compile(NLDATETIME_PATTERN)

XFERLOG_FULL_PATTERN = r'(?P<transfer_time>[^ ]+) (?P<remote_host>[^ ]+) (?P<file_size>[^ ]+) (?P<filename>[^ ]+) (?P<transfer_type>[^ ]+) (?P<special_action_flag>[^ ]+) (?P<direction>[^ ]+) (?P<access_mode>[^ ]+) (?P<username>[^ ]+) (?P<service_name>[^ ]+) (?P<authentication_method>[^ ]+) (?P<authenticated_user_id>[^ ]+) (?P<completion_status>[^ ]+)'

xferlog_line  = 'Thu Oct 27 04:25:41 2011 0 10.10.10.176 6993 /home/eumetsat/data/groups/msg-lrit-dcp/a300042541L-000-MSG___-DCP_________-DCP______-000165___-201109270423-__.tmp b _ i r eumetsat ftp 0 * c'
xferlog_line1 = 'Thu Oct 27 04:26:01 2011 1 10.10.10.176 17346948 /home/eumetsat/data/gnc-us/groups/gnc-us-ranet/a300042357ranet_4_GCS32061248146588.zip.tmp b _ i r eumetsat ftp 0 * c'

XFERLOG_DATE_PATTERN = r'(?P<date>(?P<wday>Mon|Tue|Wed|Thu|Fri|Sat|Sun) (?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dev) (?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])) (?P<time>([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])) (?P<year>(18|19|[2-5][0-9])\d\d))'
XFERLOG_HOST         = r'(?P<host>\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)'
XFERLOG_FILESIZE     = r'(?P<filesize>\S+)'
XFERLOG_FILENAME     = r'(?P<filename>\S+)'
XFERLOG_REST         = r'(?P<transfer_type>\S+) (?P<special_action_flag>\S+) (?P<direction>\S+) (?P<access_mode>\S+) (?P<username>\S+) (?P<service_name>\S+) (?P<authentication_method>\S+) (?P<authenticated_user_id>\S+) (?P<completion_status>\S+)'

XFERLOG_PATTERN = XFERLOG_DATE_PATTERN + r' [0|1] ' + XFERLOG_HOST + r' ' + XFERLOG_FILESIZE + r' ' + XFERLOG_FILENAME + r' ' + XFERLOG_REST

XFERLOG_RE      = re.compile(XFERLOG_PATTERN)

XFERLOG_DATE_RE           = re.compile(XFERLOG_DATE_PATTERN)

XFERLOG_TIME_PATTERN = r'(?P<day>(0[1-9]|[12][0-9]|3[01]|[1-9])) (?P<time>([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9]))'
XFERLOG_TIME_RE      = re.compile(XFERLOG_TIME_PATTERN)

def parse_xferlog_date(a_date_str):
    """
       parse xferlog date
    """
    matched = XFERLOG_RE.match(a_date_str)
        
    if matched:
        print("matched")
    else:
        print("unmatched")

def parse_xferlog(a_date_str):
    """
       parse xferlog date
    """
    matched = XFERLOG_RE.match(a_date_str)
        
    if matched:
        print("matched")
        print("filename = %s\n" %(matched.group('filename')))
    else:
        print("unmatched")



if __name__ == '__main__':

    #parse_xferlog_date('Thu Oct 27 04:25:26 2011 0 10.10.10.176 2061 /home/eumetsat/data/retim/groups/retim-4211/a300042526LFPW00232111.20110927042506_P4211PT8AAF_RAFARAPID.2061.b.tmp b _ i r eumetsat ftp 0 * c')
    d = datetime.datetime.strptime('Oct 27 04:26:01 2011', '%b %d %H:%M:%S %Y')
    print d
    #parse_xferlog(xferlog_line1)