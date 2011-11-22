'''
Created on Nov 3, 2011

@author: gaubert
'''

import os
import string
import datetime
import sys
import re

import multitail
import tellicastlog_parser
import xferlog_parser

import eumetsat.dmon.common.mem_db as mem_db
import eumetsat.dmon.common.time_utils as time_utils

def print_table(a_db):
    """
      print a table
    """
    header_Active   = "--Active----------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    header_Finished = "--Finished--------------------------------------------------------------------------------------------------------------------------------------------------------\n"
    
    header          = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |     finished    |\n"
    
    template = "%s|%s|%s|%s|%s|%s|%s|\n"
    
    active_data = header_Active   + header
    finish_data = header_Finished + header
    
    for record in a_db:
        
        #reduce filename and jobname size to 50
        filename = record['filename']
        if filename:
            filename = os.path.basename(filename)
            
            #will not fail if name < 50
            filename = filename[:50]
        else:
            filename = "-"
        
        jobname = record['jobname']
        if jobname:
            #will not fail if name < 20
            jobelems = jobname.split('-')
            jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
        else:
            jobname = "-"
        
        uplinked = record.get('uplinked', None)
        if not uplinked:
            uplinked = "-"
        else:
            uplinked = time_utils.datetime_to_compactdate(uplinked)
            
        queued   = record.get('queued', None)
        if not queued:
            queued = "-"
        else:
            queued = time_utils.datetime_to_compactdate(queued)
        
        annouc   = record.get('announced', None)
        if not annouc:
            annouc = "-"
        else:
            annouc = time_utils.datetime_to_compactdate(annouc)
            
        blocked   = record.get('blocked', None)
        if not blocked:
            blocked = "-"
        else:
            blocked = time_utils.datetime_to_compactdate(blocked)
            
        finished = record.get('finished', None)
        if not finished:
            finished = "-"
        else:
            finished = time_utils.datetime_to_compactdate(finished)
            
        if finished == '-':
            active_data += template % (string.center(filename,50), string.center(uplinked,17),\
                          string.center(queued, 17),string.center(jobname, 20), \
                          string.center(blocked, 17),  string.center(annouc, 17),\
                          string.center(finished, 17))
        else:
            finish_data += template % (string.center(filename,50), string.center(uplinked,17),\
                          string.center(queued, 17),string.center(jobname, 20), \
                          string.center(blocked, 17),  string.center(annouc, 17),\
                          string.center(finished, 17))
        
       
    print("%s\n%s" %(active_data, finish_data) )
    
    

def old_print_table(a_db):
    """
      print a table
    """
    header_l = "------------------------------------------------------------------------------------------------------------------------------------------------------------------"
    header   = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |     finished    |"
    template = "%s|%s|%s|%s|%s|%s|%s|"
    
    print(header)
    
    for record in a_db:
        
        #reduce filename and jobname size to 50
        filename = record['filename']
        if filename:
            filename = os.path.basename(filename)
            
            #will not fail if name < 50
            filename = filename[:50]
        else:
            filename = "-"
        
        jobname = record['jobname']
        if jobname:
            #will not fail if name < 20
            jobelems = jobname.split('-')
            jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
        else:
            jobname = "-"
        
        uplinked = record.get('uplinked', None)
        if not uplinked:
            uplinked = "-"
        else:
            uplinked = time_utils.datetime_to_compactdate(uplinked)
            
        queued   = record.get('queued', None)
        if not queued:
            queued = "-"
        else:
            queued = time_utils.datetime_to_compactdate(queued)
        
        annouc   = record.get('announced', None)
        if not annouc:
            annouc = "-"
        else:
            annouc = time_utils.datetime_to_compactdate(annouc)
            
        blocked   = record.get('blocked', None)
        if not blocked:
            blocked = "-"
        else:
            blocked = time_utils.datetime_to_compactdate(blocked)
            
        finished = record.get('finished', None)
        if not finished:
            finished = "-"
        else:
            finished = time_utils.datetime_to_compactdate(finished)
        
        print(template % (string.center(filename,50), string.center(uplinked,17),\
                          string.center(queued, 17),string.center(jobname, 20), \
                          string.center(blocked, 17),  string.center(annouc, 17),\
                          string.center(finished, 17)))
    
    print(header_l)
    
    
#regular expression to read aggregated info
process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 
expr_re = re.compile(process_expr)

def get_dwd_record(db, result, dirmon_dir):
    """
       Manage the particular case of DWD records
    """  
    #define type dirmon_dir -> ftp user
    if dirmon_dir == 'wmo-ra6':
        type = 'wmora6'
    else:
        type = 'dwd'
    
    records = db(filename = result['file'])
    
    for rec in records:
        if rec['metadata'].get('ftp_user') == type:
            return [rec]
    
    return []


# global to the module
s_parser = tellicastlog_parser.TellicastLogParser('tc-send')
x_parser = xferlog_parser.XferlogParser()
d_parser = tellicastlog_parser.TellicastLogParser('dirmon')
    
mapper = {'xferlog'   : 'xferlog',
          'send.log'  : 'tc-send',
          'dirmon.log' : 'dirmon'}

def analyze_and_print(db, line, filename):
    """
       Analysis from the line and filename
    """
    
    the_type = mapper[filename]
            
    if the_type == 'xferlog':
        result = x_parser.parse_one_line(line)
        
        #add file in db
        db.insert(filename = result['file'],uplinked = result['time'], metadata = result['metadata'])
        
    elif the_type == 'dirmon':
        result = d_parser.parse_one_line(line)
        
        if result.get('job_status', None) == 'created':
            
            dirmon_dir = result['metadata']['dirmon_dir']
            #special case for DWD (should hopefully disappear in the future
            if dirmon_dir == 'wmo-ra6' or dirmon_dir.startswith('DWD'):
                records = get_dwd_record(db, result, dirmon_dir)
                            
            else:       
            
                records = db(filename = result['file'])
                
            if len(records) == 0:
                #no file created so it means that the xferlog message has not been received
                # add it in the table
                db.insert(filename=result['file'], jobname = result['job'], queued = result['time'], metadata = result['metadata'])
            else:
                for rec in records:
                                                                                
                    r_job = db(jobname = result['job'])
                    
                    #if job reconcile both info
                    if r_job:
                        
                        #update filename info
                        db.update(rec, queued = result['time'], jobname = r_job[0]['jobname'], announced = r_job[0]['announced'], finished = r_job[0]['finished'])  
                        
                        #delete job record
                        db.delete(r_job[0])
                        
                    else:
                        #no other record with job name, update record
                        db.update(rec, jobname = result['job'], queued = result['time'])                
            
    elif the_type == 'tc-send':
        result = s_parser.parse_one_line(line)
        
        # look for job_status == job_announced
        if result.get('job_status') == 'announced':
            
            # get all records concerned by this job
            records = db(jobname = result.get('job', None))
            
            if len(records) == 0:
                # add a line in the to print table
                db.insert(jobname = result.get('job', None), announced = result['time'])
            else:
                for rec in records:
                   #found a job so update this line in db
                   db.update(rec, jobname = result.get('job', None), announced = result['time']) 
                   
        elif result.get('job_status') == 'blocked':
            
            #get all records concerned by this job
            records = db(jobname = result.get('job', None))
            
            if len(records) == 0:
                # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                db.insert(jobname = result.get('job', None), blocked = result['time'])
            else:
                for rec in records:
                    # update info with finished time
                    db.update(rec, blocked = result['time']) 
        elif result.get('job_status') == 'finished':

            #get all records concerned by this job
            records = db(jobname = result.get('job', None))
            
            if len(records) == 0:
                # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                db.insert(jobname = result.get('job', None), finished = result['time'])
            else:
                for rec in records:
                    # update info with finished time
                    db.update(rec, finished = result['time'])    
            
            
    #print table
    print_table(db)
    
def analyze_from_aggregated_file():
    """
       Analyze from an aggregated file containing xferlog, dirmon.log and send.log
    """
    iter = open('/tmp/logfile.log')
    
    # create database
    db = mem_db.Base('analysis')
     # create new base with field names (set mode = open) to overwrite db on next run
    db.create('filename', 'uplinked', \
              'queued', 'jobname', \
              'announced','blocked', \
              'finished','metadata', mode = 'open')
    
    
    for elem in iter:
        #process only tuples (other lines should be ignored)
        matched = expr_re.match(elem)
        if matched:
             
            line     = matched.group('line')
            filename = matched.group('filename')
            
            analyze_and_print(db, line, filename)
    

def analyze_from_multiple_files():
    """
       Analyze
    """
    file_send    = open('/tmp/send.log')
    file_xferlog = open('/tmp/xferlog')
    file_dirmon  = open('/tmp/dirmon.log')
    
    iter = multitail.MultiFileTailer.tail([file_send, file_xferlog, file_dirmon])
    
    # create database
    db = mem_db.Base('analysis')
     # create new base with field names (set mode = open) to overwrite db on next run
    db.create('filename', 'uplinked', \
              'queued', 'jobname', \
              'announced','blocked', \
              'finished','metadata', mode = 'open')
    
    for (line, filename) in iter:
        
        analyze_and_print(db, line, filename)
    
    
if __name__ == '__main__': 
    str = "('VRB:2011-11-21 13:14:15.075:Content for job \"retim-4030-36515-2011-11-21-13-14-09-497.job\" on channel \"MFRAFRG6\" is announced.', 'send.log')" 
     
    analyze_from_aggregated_file()