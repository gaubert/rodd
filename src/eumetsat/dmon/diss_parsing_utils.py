'''
Created on Nov 9, 2011

@author: guillaume.aubert@eumetsat.int
'''
import re
import os

XFERLOG    = r'.*xferlog:.*'
XFERLOG_RE = re.compile(XFERLOG)
DIRMON    = r'.*dirmon.log:.*'
DIRMON_RE = re.compile(DIRMON)
TCSEND    = r'.*send.log:.*'
TCSEND_RE = re.compile(TCSEND)
GEMS      = r'.*GEMS.logging:.*'
GEMS_RE   = re.compile(GEMS)

GUESS = { 
          'xferlog' : XFERLOG_RE,
          'dirmon'  : DIRMON_RE, 
          'tc-send'  : TCSEND_RE,
          'gems'    : GEMS_RE,
        }

def guess_app(a_record):
    """
       Guess if a record is xferlog, send.log or dirmon.log
    """
    
    for (key, val) in GUESS.items():
        if val.match(a_record):
            return key
    
    return None

def get_xferlog_file_info(a_file_path):
    """
       Get the short filename from the full file path and get the service directory where it goes
    """
    filename    = os.path.basename(a_file_path)
    
    #try to get the service dir
    f_dir = os.path.basename(os.path.dirname(a_file_path))
    if f_dir == 'groups':
        dname = os.path.dirname(a_file_path)
        pos   = dname.rfind('/')
        f_dir = os.path.basename(dname[:pos])
    
    return (filename, f_dir)

def get_human_readable_bytes(a_bytes):
    """
       Return a string of human readable bytes in Kilo, Mega, Giga
    """
    bytes = float(a_bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fTB' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fGB' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fMB' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fKB' % kilobytes
    else:
        size = '%.2fB' % bytes
    return size



    