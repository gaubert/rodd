'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''

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

class Analyzer(object):
    """
       Analyze uplink server logs and display results on screen
    """
    LOG = log_utils.LoggerFactory.get_logger('Analyzer')
    
    #regular expression to read aggregated info
    process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 
    expr_re = re.compile(process_expr)
    
    # global to the module
    s_parser = tellicastlog_parser.TellicastLogParser('tc-send')
    x_parser = xferlog_parser.XferlogParser()
    d_parser = tellicastlog_parser.TellicastLogParser('dirmon')
        
    mapper = {'xferlog'   : 'xferlog',
              'send.log'  : 'tc-send',
              'dirmon.log' : 'dirmon'}
        
    def __init__(self):
        """
           constructor
        """
        # create database
        self.mem_db = mem_db.Base('analysis')
        # create new base with field names (set mode = open) to overwrite db on next run
        #keep X elements max in collections
        self.mem_db.create('filename', 'uplinked', \
                  'queued', 'jobname', \
                  'announced','blocked', \
                  'finished','metadata', 'last_update', 'finished_time_insert', mode = 'override', capped_size=1000000)
        
        self.mem_db.create_index('last_update')
        
        #display = displays.TextDisplay()
        self.display = displays.CurseDisplay()
        
    def get_dwd_record(self, database, result, dirmon_dir): #pylint: disable-msg=R0201
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

    def remove_expired_records(self, database): #pylint: disable-msg=R0201
        """
           remove records that have been finished for more than 60 seconds
        """
        expiry_time = 0 # 20 in seconds
        now = datetime.datetime.now()
        
        Analyzer.LOG.info("Before to remove records")
        #self.print_db_logfile(database)
        
        removed_rec = 0
        for rec in [ r for r in database \
                    if ( r.get('finished_time_insert', None) and (now - r['finished_time_insert']) > datetime.timedelta(seconds=expiry_time) )\
                   ]:
            database.delete(rec)
            Analyzer.LOG.info("deleted %s" % (rec) )
            removed_rec += 1
        
        if removed_rec > 0:
            Analyzer.LOG.info("Deleted %d records" % (removed_rec))
            Analyzer.LOG.info("After to remove records")
            self.print_db_logfile(database)
            
        

    def print_db_logfile(self, database): #pylint: disable-msg=R0201
        """
          print database in log file for debuging purposes
        """
        for rec in database:
            Analyzer.LOG.info(rec)
           

    def analyze(self, database, line, filename):
        """
           Analysis from the line and filename
        """
        
        the_type = Analyzer.mapper[filename]
                
        if the_type == 'xferlog':
            result = Analyzer.x_parser.parse_one_line(line)
            
            #add file in db
            database.insert(filename = result['file'], \
                            uplinked = result['time'], \
                            metadata = result['metadata'], \
                            last_update= datetime.datetime.now())
            
        elif the_type == 'dirmon':
            result = Analyzer.d_parser.parse_one_line(line)
            
            if result.get('job_status', None) == 'created':
                
                dirmon_dir = result['metadata']['dirmon_dir']
                #special case for DWD (should hopefully disappear in the future
                if dirmon_dir == 'wmo-ra6' or dirmon_dir.startswith('DWD'):
                    records = self.get_dwd_record(database, result, dirmon_dir)
                                
                else:       
                
                    records = database(filename = result['file'])
                    
                if len(records) == 0:
                    #no file created so it means that the xferlog message has not been received
                    # add it in the table
                    database.insert(filename=result['file'], \
                                    jobname = result['job'], \
                                    queued = result['time'], \
                                    metadata = result['metadata'], last_update= datetime.datetime.now())
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
            result = Analyzer.s_parser.parse_one_line(line)
            
            # look for job_status == job_announced
            if result.get('job_status') == 'announced':
                
                # get all records concerned by this job
                records = database(jobname = result.get('job', None))
                
                if len(records) == 0:
                    # add a line in the to print table
                    database.insert(jobname = result.get('job', None), \
                                    announced = result['time'], last_update= datetime.datetime.now())
                else:
                    for rec in records:
                        #found a job so update this line in db
                        database.update(rec, jobname = result.get('job', None), \
                                        announced = result['time'], last_update= datetime.datetime.now()) 
                       
            elif result.get('job_status') == 'blocked':
                
                #get all records concerned by this job
                records = database(jobname = result.get('job', None))
                
                if len(records) == 0:
                    # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                    database.insert(jobname = result.get('job', None), \
                                    blocked = result['time'], last_update= datetime.datetime.now())
                else:
                    for rec in records:
                        # update info with finished time
                        database.update(rec, blocked = result['time']) 
                        
            elif result.get('job_status') == 'finished':
    
                #get all records concerned by this job
                records = database(jobname = result.get('job', None))
                
                if len(records) == 0:
                    # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                    database.insert(jobname = result.get('job', None), \
                                    finished = result['time'], \
                                    finished_time_insert = datetime.datetime.now(), \
                                    last_update= datetime.datetime.now())
                else:
                    for rec in records:
                        # update info with finished time
                        database.update(rec, finished = result['time'], \
                                        finished_time_insert = datetime.datetime.now(), \
                                        last_update= datetime.datetime.now())   
         
                    
    def print_on_display(self, a_display, a_last_time_display):  #pylint: disable-msg=R0201
        """
           Display every x seconds
        """ 
        current_time = datetime.datetime.now()
        if not a_last_time_display:
            a_display.print_screen(self.mem_db, current_time)
            return current_time
        else:
            if current_time - a_last_time_display > datetime.timedelta(seconds=2):
                
                #clean database 
                self.remove_expired_records(self.mem_db)
                
                a_display.print_screen(self.mem_db, current_time)
                return current_time
            else:
                return a_last_time_display
    
    def analyze_from_tailed_file(self, a_file_paths):
        """
           Analyze from an aggregated file containing xferlog, dirmon.log and send.log
        """
        files = []
        for f_path in a_file_paths:
            files.append(open(f_path, 'r'))
        
        f_iter = multitail.MultiFileTailer.tail(files)
        
        last_time_display = None
        on_error = False
        
        try:
            
            #init print
            self.print_on_display(self.display, None)
        
            for (f_line, _) in f_iter:
                
                #process only tuples (other lines should be ignored)
                matched = Analyzer.expr_re.match(f_line)
                if matched:
                     
                    line     = matched.group('line')
                    filename = matched.group('filename')
                    
                    # sometimes the tail can eat (bug) part of the line
                    # ignore this exception
                    try:
                        self.analyze(self.mem_db, line, filename)
                    except tellicastlog_parser.InvalidTellicastlogFormatError, err:
                        error_str = utils.get_exception_traceback()
                        Analyzer.LOG.error("Parser Exception %s, traceback %s" %(err, error_str))
                    
                    last_time_display = self.print_on_display(self.display, last_time_display)
                    
                    kb_input = self.display.check_for_input()
                    if kb_input and kb_input == 'QUIT':
                        break # quit loop
                        
            else:
                #force update
                self.print_on_display(self.mem_db, self.display, None)
            
            Analyzer.LOG.info("Out of loop")
                    
                    
        except KeyboardInterrupt:
            
            #CTRL^C pressed so silently quit
            sys.exit(0)
        except Exception, err:
            
            Analyzer.LOG.error("In Error")
            
            error_str = utils.get_exception_traceback()
            
            Analyzer.LOG.error("received error %s. Traceback = %s" %(err, error_str))
            
            on_error = True
        finally:
            #whatever the case always reset the screen
            self.display.reset_screen()
            if on_error:
                print("Exiting on error")
                return 1  #pylint: disable-msg=W0150
            else:
                print("Exiting gracefully")
                return 0  #pylint: disable-msg=W0150
    
if __name__ == '__main__': 
    
    log_utils.LoggerFactory.setup_simple_file_handler('/tmp/analyze.log') 
    
    analyzer = Analyzer() #pylint: disable-msg=C0103
    
    sys.exit(analyzer.analyze_from_tailed_file(['/tmp/logfile.log']))