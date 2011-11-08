'''
Created on Nov 2, 2011

@author: guillaume.aubert@eumetsat.int
'''
import tellicastlog_parser as tellicast
from sandbox.dmon.tellicastlog_parser import TellicastLogParser


def gap_finder(a_files, a_seconds):
    '''
       Find gaps of more than x secs between log lines
       Args:
           a_files: list of files
    '''
    
    result = []
    
    parser = tellicast.TellicastLogParser()
    
    for file in a_files:
        parser.set_lines_to_parse(file)
        first_tok = parser.next()
        print("parse\n")
        for token in parser:
            sec_tok = token
            
            diff    = sec_tok['time'] - first_tok['time']
            
            seconds = (diff.days*86400) + diff.seconds + (diff.microseconds* 0.000001)
            
            if seconds >= a_seconds:
                result.append({'file'        : file.name,
                               'first_line'  : first_tok['full_msg'][:-1],
                               'second_line' : sec_tok['full_msg'][:-1],
                               'gap_in_sec'  : seconds
                              })
            
            first_tok = sec_tok
    
    return result
            
if __name__ == '__main__':
    
    test_file = '/homespace/gaubert/logs/tests/send_test.log'
    send_log   = '/homespace/gaubert/logs/tests/send.log'
    send_log1  = '/homespace/gaubert/logs/tests/send.log.1'
    
    #files = [open(test_file),open(test_file)]
    files = [open(send_log),open(send_log1)]
    
    #look for gaps of one second
    result = gap_finder(files, 3)
    
    if result:
        for elem in result:
            print("elem = %s\n" %(elem))
    else:
        print("no elems found")
    