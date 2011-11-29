'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''

import os
import datetime
import sys
import re

import multitail
import tellicastlog_parser
import xferlog_parser

import eumetsat.dmon.common.mem_db as mem_db
import eumetsat.dmon.common.utils as utils
import eumetsat.dmon.common.log_utils  as log_utils

import eumetsat.dmon.displays as displays


import time


    
    
#regular expression to read aggregated info
process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 
expr_re = re.compile(process_expr)

def get_dwd_record(database, result, dirmon_dir):
    """
       Manage the particular case of DWD records
    """  
    #define type dirmon_dir -> ftp user
    if dirmon_dir == 'wmo-ra6':
        msg_type = 'wmora6'
    else:
        msg_type = 'dwd'
    
    records = database(filename = result['file'])
    
    for rec in records:
        if rec['metadata'].get('ftp_user') == msg_type:
            return [rec]
    
    return []


# global to the module
s_parser = tellicastlog_parser.TellicastLogParser('tc-send')
x_parser = xferlog_parser.XferlogParser()
d_parser = tellicastlog_parser.TellicastLogParser('dirmon')
    
mapper = {'xferlog'   : 'xferlog',
          'send.log'  : 'tc-send',
          'dirmon.log' : 'dirmon'}

def remove_expired_records(database):
    """
       remove records that have been finished for more than 60 seconds
    """
    expiry_time = 20 #in seconds
    now = datetime.datetime.now()
    
    removed_rec = 0
    for rec in [ r for r in database \
                if ( r.get('finished_time_insert', None) and (now - r['finished_time_insert']) > datetime.timedelta(seconds=expiry_time) )\
               ]:
        database.delete(rec)
        removed_rec += 1
    
    if removed_rec > 0:
        LOG.info("Deleted %d records" % (removed_rec))

def print_db_logfile(database):
    """
      print database in log file for debuging purposes
    """
    for rec in database:
        LOG.info(rec)
           

def analyze(database, line, filename):
    """
       Analysis from the line and filename
    """
    
    the_type = mapper[filename]
            
    if the_type == 'xferlog':
        result = x_parser.parse_one_line(line)
        
        #add file in db
        database.insert(filename = result['file'],uplinked = result['time'], metadata = result['metadata'], last_update= datetime.datetime.now())
        
    elif the_type == 'dirmon':
        result = d_parser.parse_one_line(line)
        
        if result.get('job_status', None) == 'created':
            
            dirmon_dir = result['metadata']['dirmon_dir']
            #special case for DWD (should hopefully disappear in the future
            if dirmon_dir == 'wmo-ra6' or dirmon_dir.startswith('DWD'):
                records = get_dwd_record(database, result, dirmon_dir)
                            
            else:       
            
                records = database(filename = result['file'])
                
            if len(records) == 0:
                #no file created so it means that the xferlog message has not been received
                # add it in the table
                database.insert(filename=result['file'], jobname = result['job'], queued = result['time'], metadata = result['metadata'], last_update= datetime.datetime.now())
            else:
                for rec in records:
                                                                                
                    r_job = database(jobname = result['job'])
                                      
                    #if job reconcile both info
                    if r_job:
                        
                        #update filename info
                        database.update(rec, queued = result['time'], \
                                  jobname = r_job[0]['jobname'], \
                                  announced = r_job[0]['announced'], \
                                  finished = r_job[0]['finished'])  
                        
                        #delete job record
                        database.delete(r_job[0])
                        
                    else:
                        #no other record with job name, update record
                        database.update(rec, jobname = result['job'], queued = result['time'], last_update= datetime.datetime.now())              
            
    elif the_type == 'tc-send':
        result = s_parser.parse_one_line(line)
        
        # look for job_status == job_announced
        if result.get('job_status') == 'announced':
            
            # get all records concerned by this job
            records = database(jobname = result.get('job', None))
            
            if len(records) == 0:
                # add a line in the to print table
                database.insert(jobname = result.get('job', None), announced = result['time'], last_update= datetime.datetime.now())
            else:
                for rec in records:
                    #found a job so update this line in db
                    database.update(rec, jobname = result.get('job', None), announced = result['time'], last_update= datetime.datetime.now()) 
                   
        elif result.get('job_status') == 'blocked':
            
            #get all records concerned by this job
            records = database(jobname = result.get('job', None))
            
            if len(records) == 0:
                # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                database.insert(jobname = result.get('job', None), blocked = result['time'], last_update= datetime.datetime.now())
            else:
                for rec in records:
                    # update info with finished time
                    database.update(rec, blocked = result['time']) 
        elif result.get('job_status') == 'finished':

            #get all records concerned by this job
            records = database(jobname = result.get('job', None))
            
            if len(records) == 0:
                # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                database.insert(jobname = result.get('job', None), finished = result['time'], finished_time_insert = datetime.datetime.now(), last_update= datetime.datetime.now())
            else:
                for rec in records:
                    # update info with finished time
                    database.update(rec, finished = result['time'], finished_time_insert = datetime.datetime.now(), last_update= datetime.datetime.now())   
                    
def print_on_display(a_db, a_display, a_last_time_display):
    """
       Display every x seconds
    """ 
    if not a_last_time_display:
        a_display.print_screen(a_db)
        return datetime.datetime.now()
    else:
        current_time = datetime.datetime.now()
        if current_time - a_last_time_display > datetime.timedelta(seconds=2):
            a_display.print_screen(a_db)
            return datetime.datetime.now()
        else:
            return a_last_time_display
    
def analyze_from_tailed_file():
    """
       Analyze from an aggregated file containing xferlog, dirmon.log and send.log
    """
    agregfile = open('/tmp/logfile.log', 'r')
    
    iter = multitail.MultiFileTailer.tail([agregfile])
    
    # create database
    db = mem_db.Base('analysis')
    # create new base with field names (set mode = open) to overwrite db on next run
    #keep X elements max in collections
    db.create('filename', 'uplinked', \
              'queued', 'jobname', \
              'announced','blocked', \
              'finished','metadata', 'last_update', 'finished_time_insert', mode = 'override', capped_size=1000000)
    
    db.create_index('last_update')
    
    #display = displays.TextDisplay()
    display = displays.CurseDisplay()
    
    last_time_display = None
    on_error = False
    
    try:
        
        #init print
        print_on_display(db, display, None)
    
        for (f_line, _) in iter:
            
            #process only tuples (other lines should be ignored)
            matched = expr_re.match(f_line)
            if matched:
                 
                line     = matched.group('line')
                filename = matched.group('filename')
                
                # sometimes the tail can eat (bug) part of the line
                # ignore this exception
                try:
                    analyze(db, line, filename)
                except tellicastlog_parser.InvalidTellicastlogFormatError, e:
                    error_str = utils.get_exception_traceback()
                    LOG.error("Parser Exception %s, traceback %s" %(e, error_str))
                
                last_time_display = print_on_display(db, display, last_time_display)
                
                input = display.check_for_input()
                if input and input == 'QUIT':
                    break # quit loop
                
                remove_expired_records(db)
                    
        else:
            #force update
            print_on_display(db, display, None)
        
        LOG.info("Out of loop")
                
                
    except KeyboardInterrupt:
        
        #CTRL^C pressed so silently quit
        sys.exit(0)
    except Exception, e:
        
        LOG.error("In Error")
        
        error_str = utils.get_exception_traceback()
        
        LOG.error("received error %s. Traceback = %s" %(e,error_str))
        
        on_error = True
    finally:
        #whatever the case always reset the screen
        display.reset_screen()
        if on_error:
            print("Exiting on error")
            sys.exit(1)
        else:
            print("Exiting gracefully")
            sys.exit(0)
 
def analyze_from_multiple_files():
    """
       Analyze
    """
    file_send    = open('/tmp/send.log')
    file_xferlog = open('/tmp/xferlog')
    file_dirmon  = open('/tmp/dirmon.log')
    
    iterable = multitail.MultiFileTailer.tail([file_send, file_xferlog, file_dirmon])
    
    # create database
    database = mem_db.Base('analysis')
    # create new base with field names (set mode = open) to overwrite db on next run
    database.create('filename', 'uplinked', \
              'queued', 'jobname', \
              'announced','blocked', \
              'finished','metadata', mode = 'override')
    
    for (line, filename) in iterable:
        
        analyze(database, line, filename)
    
    
if __name__ == '__main__': 
    
    log_utils.LoggerFactory.setup_simple_file_handler('/tmp/analyze.log') 
    
    LOG = log_utils.LoggerFactory.get_logger('ALogger')
    
    LOG.info("start")
     
    #analyze_from_aggregated_file()
    analyze_from_tailed_file()