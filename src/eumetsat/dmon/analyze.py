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
import re

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
            
            #will not fail if name < 20
            filename = filename[:20]
        else:
            filename = "-"
        
        jobname = a_to_print[3]
        if jobname:
            #will not fail if name < 20
            jobelems = jobname.split('-')
            jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
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
    
process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 
expr_re = re.compile(process_expr)
    
def analyze_from_aggregated_file():
    """
       Analyze from an aggregated file containing xferlog, dirmon.log and send.log
    """
    iter = open('/tmp/logfile.log')
    
    s_parser = tellicastlog_parser.TellicastLogParser('tc-send')
    x_parser = xferlog_parser.XferlogParser()
    d_parser = tellicastlog_parser.TellicastLogParser('dirmon')
    
    mapper = {'xferlog'   : 'xferlog',
              'send.log'  : 'tc-send',
              'dirmon.log' : 'dirmon'}
     
    to_print    = []
    waiting_job = {}
    file_index = {}
    job_index  = {}
    
    for elem in iter:
        #process only tuples (other lines should be ignored)
        matched = expr_re.match(elem)
        if matched:
            #print("filename %s, line %s \n" %(filename, line))
            
            line     = matched.group('line')
            filename = matched.group('filename')
            
            the_type = mapper[filename]
            
            if the_type == 'xferlog':
                result = x_parser.parse_one_line(line)
                
                #add file
                res = [result['file'], datetime_to_str(result['time']), None , None, None, None]
                
                to_print.append(res)
                
                # store poistion in the list
                file_index[result['file']] = len(to_print) - 1
                
                #print table
                print_table(to_print)
                
            elif the_type == 'dirmon':
                result = d_parser.parse_one_line(line)
                if result.get('job_status', None) == 'created':
                    pos = file_index.get(result['file'], -1)
                    if pos >= 0:
                        
                        # update info with queued status
                        info =  to_print[pos]
                        
                        #check if there is already a job within waiting list
                        job_info = waiting_job.get(result['job'], None)
                        
                        #if job reconcile both info
                        if job_info:
                            info = [info[0], info[1], datetime_to_str(result['time']), job_info[3], job_info[4], job_info[5]]
                            del waiting_job[result['job']]
                        else:
                            info = [info[0], info[1], datetime_to_str(result['time']), None, None, None]
                              
                        # update to_print list              
                        to_print[pos] = info
                          
                        #update indexes
                        file_index[result['file']] = pos
                        job_index[result['job']]   = pos
                                             
                    else:
                        
                        #no file created so it means that the xferlog message has not been received
                        
                        # add it in the table
                        info = [result['file'], None , datetime_to_str(result['time']), result['job'], None, None]
                        
                        to_print.append(info)
                        
                        #update indexes
                        file_index[result['file']] = len(to_print) - 1
                        job_index[result['job']]   = len(to_print) - 1
                        
                    #print table
                    print_table(to_print)
                    
            elif the_type == 'tc-send':
                result = s_parser.parse_one_line(line)
                
                # look for job_status == job_announced
                if result.get('job_status') == 'announced':
                    #try to find the job in the index 
                    pos = job_index.get(result.get('job', None))
                    if pos >= 0:
                        
                        #get the line in the file_index
                        info = to_print[pos]
                        
                        # update info with announced status and job name
                        info  = [info[0], info[1], info[2], result.get('job', None), datetime_to_str(result['time']), None]
                        
                        to_print[pos]=info
                        
                        #update indexes
                        file_index[info[0]] = pos
                        job_index[result['job']]   = pos
                        
                    else:
                        
                        #no dirmon message received so add job in waiting list of jobs for the moment
                        
                        # add a line in the to print table
                        info = [None, None, None, result.get('job', None), datetime_to_str(result['time']), None]
                        
                        waiting_job[result['job']] = info
                    
                    #print table
                    print_table(to_print)
                    
                elif result.get('job_status') == 'finished':
                    #try to find the job in the index 
                    pos = job_index.get(result.get('job',None))
                    
                    if pos >= 0:
                        info = to_print[pos]
                        
                        # update info with announced status and job name
                        info  = [info[0], info[1], info[2], info[3], info[4], datetime_to_str(result['time'])]  
                        
                        to_print[pos] = info
                        
                        #update indexes
                        job_index[result['job']]   = len(to_print) - 1
                        
                    else:
                        
                        j_info = waiting_job.get(result['job'], None)
                        
                        if j_info:
                            j_info[5] = datetime_to_str(result['time'])
                            waiting_job[result['job']] = j_info
                        else:
                            # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                            info = [None, None, None, result.get('job', None), None, datetime_to_str(result['time'])]
                            waiting_job[result['job']] = info
                    
                    #print table
                    print_table(to_print)
    

def analyze_from_multiple_files():
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
    
    iter = multitail.MultiFileTailer.tail([file_send, file_xferlog, file_dirmon])
    
    to_print    = []
    waiting_job = {}
    file_index = {}
    job_index  = {}
    
    """iter = [("Thu Oct 27 04:25:28 2011 0 10.10.10.176 37737 /home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE b _ i r eumetsat ftp 0 * c",'/tmp/xferlog'),\
            ("Thu Oct 27 04:25:28 2011 0 10.10.10.176 37737 /home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE2 b _ i r eumetsat ftp 0 * c",'/tmp/xferlog'),\
             ("VRB:2011-10-27 03:59:40.995:Adding file '/home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE' to job 'MYJOB-01', last modified: 2011-10-27 03:59:34, size: 26423",'/tmp/dirmon.log'),\
             ('VRB:2011-10-26 21:02:36.439:Content for job "MYJOB-01" on channel "MFRAFRG6" is announced.',"/tmp/send.log"),\
             ("VRB:2011-10-27 03:59:40.995:Adding file '/home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE2' to job 'MYJOB-02', last modified: 2011-10-27 03:59:34, size: 26423",'/tmp/dirmon.log'),\
             ('MSG:2011-10-26 21:02:37.147:FileBroadcast job "MYJOB-01" on channel "MFRAFRG6" done',"/tmp/send.log"),\
             ("Thu Oct 27 04:25:28 2011 0 10.10.10.176 37737 /home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE3 b _ i r eumetsat ftp 0 * c",'/tmp/xferlog'),\
             ('VRB:2011-10-26 21:02:36.439:Content for job "MYJOB-03" on channel "MFRAFRG6" is announced.',"/tmp/send.log"),\
             ("VRB:2011-10-27 03:59:40.995:Adding file '/home/eumetsat/data/wmora6/groups/wmo-ra6/MYFILE3' to job 'MYJOB-03', last modified: 2011-10-27 03:59:34, size: 26423",'/tmp/dirmon.log'),\
             ('MSG:2011-10-26 21:02:37.147:FileBroadcast job "MYJOB-03" on channel "MFRAFRG6" done',"/tmp/send.log"),\
             ('VRB:2011-10-26 21:02:36.439:Content for job "MYJOB-02" on channel "MFRAFRG6" is announced.',"/tmp/send.log"),
             ('MSG:2011-10-26 21:02:37.147:FileBroadcast job "MYJOB-02" on channel "MFRAFRG6" done',"/tmp/send.log"),\
           ]
    """
    
    for (line, filename) in iter:
        #print("filename %s, line %s \n" %(filename, line))
        
        type = mapper[filename]
        
        if type == 'xferlog':
            result = x_parser.parse_one_line(line)
            
            #add file
            res = [result['file'], datetime_to_str(result['time']), None , None, None, None]
            
            to_print.append(res)
            
            # store poistion in the list
            file_index[result['file']] = len(to_print) - 1
            
            #print table
            print_table(to_print)
            
        elif type == 'dirmon':
            result = d_parser.parse_one_line(line)
            if result.get('job_status', None) == 'created':
                pos = file_index.get(result['file'], -1)
                if pos >= 0:
                    
                    # update info with queued status
                    info =  to_print[pos]
                    
                    #check if there is already a job within waiting list
                    job_info = waiting_job.get(result['job'], None)
                    
                    #if job reconcile both info
                    if job_info:
                        info = [info[0], info[1], datetime_to_str(result['time']), job_info[3], job_info[4], job_info[5]]
                        del waiting_job[result['job']]
                    else:
                        info = [info[0], info[1], datetime_to_str(result['time']), None, None, None]
                          
                    # update to_print list              
                    to_print[pos] = info
                      
                    #update indexes
                    file_index[result['file']] = pos
                    job_index[result['job']]   = pos
                                         
                else:
                    
                    #no file created so it means that the xferlog message has not been received
                    
                    # add it in the table
                    info = [result['file'], None , datetime_to_str(result['time']), result['job'], None, None]
                    
                    to_print.append(info)
                    
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
                pos = job_index.get(result.get('job', None))
                if pos >= 0:
                    
                    #get the line in the file_index
                    info = to_print[pos]
                    
                    # update info with announced status and job name
                    info  = [info[0], info[1], info[2], result.get('job', None), datetime_to_str(result['time']), None]
                    
                    to_print[pos]=info
                    
                    #update indexes
                    file_index[info[0]] = pos
                    job_index[result['job']]   = pos
                    
                else:
                    
                    #no dirmon message received so add job in waiting list of jobs for the moment
                    
                    # add a line in the to print table
                    info = [None, None, None, result.get('job', None), datetime_to_str(result['time']), None]
                    
                    waiting_job[result['job']] = info
                
                #print table
                print_table(to_print)
                
            elif result.get('job_status') == 'finished':
                #try to find the job in the index 
                pos = job_index.get(result.get('job',None))
                
                if pos >= 0:
                    info = to_print[pos]
                    
                    # update info with announced status and job name
                    info  = [info[0], info[1], info[2], info[3], info[4], datetime_to_str(result['time'])]  
                    
                    to_print[pos] = info
                    
                    #update indexes
                    job_index[result['job']]   = len(to_print) - 1
                    
                else:
                    
                    j_info = waiting_job.get(result['job'], None)
                    
                    if j_info:
                        j_info[5] = datetime_to_str(result['time'])
                        waiting_job[result['job']] = j_info
                    else:
                        # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                        info = [None, None, None, result.get('job', None), None, datetime_to_str(result['time'])]
                        waiting_job[result['job']] = info
                
                #print table
                print_table(to_print)
    
    
if __name__ == '__main__': 
    str = "('VRB:2011-11-21 13:14:15.075:Content for job \"retim-4030-36515-2011-11-21-13-14-09-497.job\" on channel \"MFRAFRG6\" is announced.', 'send.log')" 
     
    analyze_from_aggregated_file()