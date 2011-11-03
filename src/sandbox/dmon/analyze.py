'''
Created on Nov 3, 2011

@author: gaubert
'''

import multitail
import tellicastlog_parser
import xferlog_parser
import os
import string

def print_table(a_lines_to_print):
    """
      print a table
    """
    header_l = "------------------------------------------------------------------------------------"
    header   = "    Filename        |     uplinked       |       queued       |     announced      |"
    template = "%s|%s|%s|%s|"
    
    print(header)
    
    for a_to_print in a_lines_to_print:
        
        filename = os.path.basename(a_to_print[0])
        if len(filename) > 20:
            filename = filename[:20]
        
        uplinked = a_to_print[1] if a_to_print[1] else "-"
        queued   = a_to_print[2] if a_to_print[2] else "-"
        annouc   = a_to_print[3] if a_to_print[3] else "-"
        print(template % (string.center(filename,20), string.center(str(uplinked),20), string.center(queued,20), string.center(annouc,20)))
    
    print(header_l)

def analyze():
    """
       Analyze
    """
    file_send    = open('/tmp/dest.log')
    file_xferlog = open('/tmp/dest1.log')
    
    mapper = {'/tmp/dest1.log' : 'xferlog',
              '/tmp/dest.log'  : 'tc-send'}
    
    s_parser = tellicastlog_parser.TellicastLogParser('tc-send')
    x_parser = xferlog_parser.XferlogParser()
    d_parser = tellicastlog_parser.TellicastLogParser('dirmon')
    
    iter = multitail.MultiFileTailer.tail([file_send, file_xferlog])
    
    to_print = []
    index    = {}
    
    for (line, filename) in iter:
        #print("filename %s, line %s \n" %(filename, line))
        
        type = mapper[filename]
        
        if type == 'xferlog':
            result = x_parser.parse_one_line(line)
            
            #add file
            res = [result['file'], result['time'], None , None]
            to_print.append(res)
            index[result['file']] = res
            
        elif type == 'tc-send':
            result = s_parser.parse_one_line(line)
        elif type == 'dirmon':
            result = d_parser.parse_one_line(line)
        
        print_table(to_print)
            
        
        
    


if __name__ == '__main__':
    analyze()