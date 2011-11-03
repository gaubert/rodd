'''
Created on Nov 3, 2011

@author: gaubert
'''

import multitail
import tellicastlog_parser
import xferlog_parser
import os
import string
import datetime
import sys

def datetime_to_str(a_datetime):
    return a_datetime.strftime('%Y-%m-%dT%Hh%Mm%Ss')

def print_table(a_lines_to_print):
    """
      print a table
    """
    header_l = "-----------------------------------------------------------------------------------------------------------------------------"
    header   = "    filename        |     uplinked       |       queued       |       jobname      |     announced      |      finished      |"
    template = "%s|%s|%s|%s|%s|%s|"
    
    print(header)
    
    for a_to_print in a_lines_to_print:
        
        #reduce filename and jobname size to 20
        filename = a_to_print[0]
        if filename:
            filename = os.path.basename(filename)
            if len(filename) > 20:
                filename = filename[:20]
        else:
            filename = "-"
        
        jobname = a_to_print[3]
        if jobname and len(jobname) > 20:
            jobname = jobname[:20]
        else:
            jobname = "-"
        
        uplinked = a_to_print[1] if a_to_print[1] else "-"
        queued   = a_to_print[2] if a_to_print[2] else "-"
        
        annouc   = a_to_print[4] if a_to_print[4] else "-"
        finished = a_to_print[5] if a_to_print[5] else "-"
        print(template % (string.center(filename,20), string.center(uplinked,20),\
                          string.center(queued, 20),string.center(jobname, 20), \
                          string.center(annouc, 20), string.center(finished, 20)))
    
    print(header_l)

def analyze():
    """
       Analyze
    """
    file_send    = open('/tmp/send.log')
    file_xferlog = open('/tmp/xferlog')
    file_dirmon  = open('/tmp/dirmon.log')
    
    mapper = {'/tmp/xferlog'   : 'xferlog',
              '/tmp/send.log'  : 'tc-send',
              '/tmp/dirmon.log' : 'dirmon'}
    
    s_parser = tellicastlog_parser.TellicastLogParser('tc-send')
    x_parser = xferlog_parser.XferlogParser()
    d_parser = tellicastlog_parser.TellicastLogParser('dirmon')
    
    #iter = multitail.MultiFileTailer.tail([file_send, file_xferlog, file_dirmon])
    
    to_print   = []
    file_index = {}
    job_index  = {}
    
    iter = [("Thu Oct 27 04:25:28 2011 0 10.10.10.176 37737 /home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE b _ i r eumetsat ftp 0 * c",'/tmp/xferlog'),\
             ("VRB:2011-10-27 03:59:40.995:Adding file '/home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE' to job 'MYJOB-01', last modified: 2011-10-27 03:59:34, size: 26423",'/tmp/dirmon.log')]
    
    for (line, filename) in iter:
        #print("filename %s, line %s \n" %(filename, line))
        
        type = mapper[filename]
        
        if type == 'xferlog':
            result = x_parser.parse_one_line(line)
            
            #add file
            res = [result['file'], datetime_to_str(result['time']), None , None, None, None]
            
            to_print.append(res)
            
            file_index[result['file']] = len(to_print) - 1
            #print table
            print_table(to_print)
            
        elif type == 'dirmon':
            result = d_parser.parse_one_line(line)
            if result.get('job_status', None) == 'created':
                pos = file_index.get(result['file'], -1)
                if pos >= 0:
                    # update info with queued status
                    info =  to_print.pop(pos)
                    info = [info[0], info[1], datetime_to_str(result['time']), None, None, None]
                                           
                    #update indexes
                    file_index[result['file']] = pos
                    job_index[result['job']]   = pos 
                    
                    #overwrite to print
                    to_print.insert(0, info)
                                         
                else:
                    
                    # add it in the table
                    info = [result['file'], None , datetime_to_str(result['time']), None, None, None]
                    
                    to_print.insert(0, info)
                    #update indexes
                    file_index[result['file']] = len(to_print) - 1
                    job_index[result['job']]   = len(to_print) - 1
                    
                #print table
                print_table(to_print)
                
        elif type == 'tc-send':
            result = s_parser.parse_one_line(line)
            
            # look for job_status == job_announced
            if result.get('job_status') == 'announced':
                #try to find the job in the index 
                file_info = job_index.get(result.get('job',None))
                if file_info:
                    # update info with announced status and job name
                    file_info  = [file_info[0], file_info[1], file_info[2], result.get('job', None), datetime_to_str(result['time']), None]
                    
                else:
                    # add a line in the to print table
                    file_info = [None, None, None, result.get('job', None), datetime_to_str(result['time']), None]
                    job_index[result.get('job', None)] = file_info
                
                #append line in list of lines to be printed
                to_print.insert(0, file_info)
                #print table
                print_table(to_print)
            elif result.get('job_status') == 'finished':
                #try to find the job in the index 
                file_info = job_index.get(result.get('job',None))
                if file_info:
                    # update info with announced status and job name
                    file_info  = [file_info[0], file_info[1], file_info[2], file_info[3], file_info[4], datetime_to_str(result['time'])]
                    
                else:
                    # add a line in the to print table
                    file_info = [None, None, None, result.get('job', None), None, datetime_to_str(result['time'])]
                    job_index[result.get('job', None)] = file_info
                
                #append line in list of lines to be printed
                to_print.insert(0, file_info)
                #print table
                print_table(to_print)
    
    
if __name__ == '__main__':
    analyze()