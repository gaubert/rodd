'''
Created on Nov 3, 2011

@author: guillaume.aubert@eumetsat.int
'''

import datetime
import sys
import re

import pymongo

import eumetsat.dmon.common.mem_db as mem_db
import eumetsat.dmon.common.utils as utils
import eumetsat.dmon.common.log_utils  as log_utils
import eumetsat.dmon.common.analyze_utils as analyze_utils

import multitail
import tellicastlog_parser
import xferlog_parser

import eumetsat.dmon.displays as displays

class DoNothingArchiver(object):
    """
       DoNothingArchiver
    """
    def __init__(self):
        """ 
           cons
        """
        pass
    
    def connect(self, host, port):
        """
           connect method
        """
        pass
    
    def archive(self, record):
        """
           Archive 
        """
        pass
    

class Archiver(object):
    """
       MongoDB Archiver
    """
    LOG = log_utils.LoggerFactory.get_logger('Archiver')
    
    def __init__(self):
        """
           constructor
        """
        self.connection = None
        self.host = 'localhost'
        self.port = 27017
        
        self.connect(self.host, self.port)
    
    def connect(self, host, port):
        """
          connect to db
        """
        try:
            self.connection = pymongo.Connection(host, port)
        except Exception, err:
            Archiver.LOG.error("Ignore Error. Cannot connection to %s:%s" % (host, port))
            Archiver.LOG.exception(err)        
    
    def archive(self, record):
        """
           Archive finished records
        """   
        try:
            if self.connection:
                db = self.connection.diss
                Archiver.LOG.info("insert %s in mongodb" % (record))
                #clean record
                rec = { 'last_update': record['last_update'], 'created':record['created'], \
                        'metadata': record['metadata'], 'jobname': record['jobname'], \
                        'uplinked': record['uplinked'], 'finished': record['finished'],\
                        'channel': record['channel'], 'finished_time_insert': record['finished_time_insert'], 
                        'blocked': record['blocked'], 'filename': record['filename'], \
                        'queued': record['queued'], 'announced': record['announced'], \
                        'size': record['size']}
                db.records.insert(rec)
        except Exception, err:
            Archiver.LOG.error("Ignore Error. Cannot insert record in mongodb")
            Archiver.LOG.exception(err) 
            self.connection = None     
    

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
        
    def __init__(self, enable_archive = False):
        """
           constructor
        """
        # create database
        self.mem_db = mem_db.Base('analysis')
        #keep X elements max in collections
        self.mem_db.create('filename', 'uplinked', 'size', \
                  'queued', 'jobname', \
                  'announced', 'blocked', 'channel', \
                  'finished', 'metadata', 'created', 'last_update', 'finished_time_insert', capped_size=1000000)
        
        self.mem_db.create_index('last_update')
        self.mem_db.create_index('jobname')
        
        self.warn_err_db = mem_db.Base('errors')
        self.warn_err_db.create('lvl', 'msg', 'created')
        self.warn_err_db.create_index('created')
        
        self.display = displays.TextDisplay()
        #self.display = displays.CurseDisplay()
        
        #create archiver
        if enable_archive:
            self.archiver = Archiver()
        else:
            self.archiver = DoNothingArchiver()
        
        
        self._accepting_new = True
        self._sort_criteria = 'NEWEST'
        
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
        
        l_rec = []
        for rec in records:
            if rec['metadata'].get('ftp_user') == msg_type:
                l_rec.append(rec)
        
        return l_rec
    
    @classmethod
    def _rec_only_updated(cls, rec):
        """
           True if Record only updated else False
        """
        return rec.get('uplinked', None) \
               and not rec.get('queued', None) \
               and not rec.get('announced', None) \
               and not rec.get('blocked', None) \
               and not rec.get('finished', None) \
               and not rec.get('aborted', None)
        
    
    def remove_eat_upload_records(self, database):
        """
          remoce .cha and .rcv files that have been only uplinked after 5 min.
          This to not pollute the monitoring screen with eat files.
        """
        expiry_time = 180 # 3 min in seconds
        now = datetime.datetime.utcnow()
        
        for rec in [ r for r in database \
                     if ( self._rec_only_updated(r) and (r.get('filename', '').endswith('.rcv') or r.get('filename', '').endswith('.cha') \
                                                         or r.get('filename', '').endswith('.job') or r.get('filename', '').endswith('.ini')) \
                          and (now - r['created']) > datetime.timedelta(seconds=expiry_time) )\
                   ]:
            Analyzer.LOG.info("delete eat record %s" % (r.get('filename', None)))
            database.delete(rec)

    def remove_expired_records(self, database): #pylint: disable-msg=R0201
        """
           remove records that have been finished for more than 60 seconds
        """
        #special case to ignore eat files that are uploaded every day
        self.remove_eat_upload_records(database)
        
        expiry_time = 20 # 20 in seconds
        aborted_expiry_time = 43200 # 12 hours in seconds
        now = datetime.datetime.utcnow()
        
        for rec in database:
            #finished records
            if  rec.get('finished_time_insert', None) and (now - rec['finished_time_insert']) > datetime.timedelta(seconds = expiry_time) :
                #archive finished record
                self.archiver.archive(rec)
                database.delete(rec)
            #aborted for more than 12 hours records 
            elif rec.get('aborted', None) and ( now - rec.get('last_update', now) ) > datetime.timedelta(seconds = aborted_expiry_time) :
                #archive aborted record that was never finished
                self.archiver.archive(rec)
                database.delete(rec)

    def analyze(self, database, line, filename): #pylint: disable-msg=R0912,R0915
        """
           Analysis from the line and filename
        """
        
        the_type = Analyzer.mapper[filename]
                
        if the_type == 'xferlog' and self._accepting_new:
            result = Analyzer.x_parser.parse_one_line(line)
            
            #file push and action complete
            if result.get('action', None) == 'push' and result.get('completion_status', None) == 'c':
            
                #add file in db
                now = datetime.datetime.utcnow()
                database.insert(filename = result['file'], \
                                size     = long(result['file_size']), \
                                uplinked = result['time'], \
                                metadata = result['metadata'], \
                                created  = now, \
                                last_update= now)
                
            elif result.get('action', None) == 'delete':
                
                #look for a file name x in the db in order to delete it
                records = database(filename = result['file'])
                for rec in records:
                    #simply delete it at the moment
                    database.delete(rec)
                    analyze_utils.print_rec_in_logfile(rec)
            else:
                # warn in log file
                Analyzer.LOG.warning("Ignore line %s because it is a COMPLETE push or a delete file" % (line))
            
        elif the_type == 'dirmon':
            result = Analyzer.d_parser.parse_one_line(line)
            
            if result.get('job_status', None) == 'created':
                
                dirmon_dir = result['metadata']['dirmon_dir']
                #special case for DWD (should hopefully disappear in the future
                if dirmon_dir == 'wmo-ra6' or dirmon_dir.startswith('DWD'):
                    records = self.get_dwd_record(database, result, dirmon_dir)
                                
                else:       
                    records = database(filename = result['file'])
                    
                if self._accepting_new and len(records) == 0:
                    #no file created so it means that the xferlog message has not been received
                    # add it in the table
                    now = datetime.datetime.utcnow()
                    
                    database.insert(filename = result['file'], \
                                    jobname = result['job'], \
                                    queued = result['time'], \
                                    metadata = result['metadata'], created  = now, last_update= now)
                else:
                    for rec in records:
                                                                                    
                        r_job = database(jobname = result['job'])
                                          
                        #if job reconcile both info
                        if r_job and not r_job[0]['filename']:
                            
                            #update filename info
                            database.update(rec, queued = result['time'], \
                                      jobname = r_job[0]['jobname'], \
                                      announced = r_job[0]['announced'], \
                                      finished = r_job[0]['finished'])  
                            
                            #delete job record
                            database.delete(r_job[0])
                            
                        else:
                            #no other record with job name, update record
                            database.update(rec, jobname = result['job'], \
                                            queued = result['time'], \
                                            last_update = datetime.datetime.utcnow())  
                            
            elif result.get('job_status', None) == 'file_deleted': 
                #file has been deleted before to be treated
                # TO Be added in warnings db
                records = database(filename = result['file'])
                for rec in records:
                    #simply delete it at the moment
                    database.delete(rec)
                    Analyzer.LOG.warning("file %s deleted before to be jobbed" % (rec['filename']))
                    analyze_utils.print_rec_in_logfile(rec)           
                
        elif the_type == 'tc-send':
            result = Analyzer.s_parser.parse_one_line(line)
            
            # look for job_status == job_announced
            if result.get('job_status', None) == 'announced' :
                
                # get all records concerned by this job
                records = database(jobname = result.get('job', None))
                
                if self._accepting_new and len(records) == 0:
                    now = datetime.datetime.utcnow()
                    # add a line in the to print table
                    database.insert(jobname = result.get('job', None), \
                                    announced = result['time'],  created = now, last_update= now, channel = result['channel'])
                else:
                    for rec in records:
                        #found a job so update this line in db
                        database.update(rec, jobname = result.get('job', None), \
                                        announced = result['time'],last_update= datetime.datetime.utcnow(), channel = result['channel']) 
                       
            elif result.get('job_status', None) == 'blocked':
                
                #get all records concerned by this job
                records = database(jobname = result.get('job', None))
                
                if self._accepting_new and len(records) == 0:
                    now = datetime.datetime.utcnow()
                    # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                    database.insert(jobname = result.get('job', None), \
                                    blocked = result['time'], created = now, last_update= now, channel = result['channel'])
                else:
                    for rec in records:
                        # update info with blocked time
                        database.update(rec, blocked = result['time'], channel = result['channel']) 
            elif result.get('job_status', None) == 'aborted':
                # flag it as aborted and if it is aborted again update the update time
                #get all records concerned by this job
                records = database(jobname = result.get('job', None))
                
                if self._accepting_new and len(records) == 0:
                    now = datetime.datetime.utcnow()
                   
                    # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                    # put it in finish at the moment but it should be treated differently
                    database.insert(jobname = result.get('job', None), \
                                    aborted = result['time'], \
                                    created = now, \
                                    last_update= now, channel = result['channel'])
                else:
                    for rec in records:
                        # update info with finished time
                        database.update(rec, aborted = result['time'], \
                                        last_update= datetime.datetime.utcnow(), channel = result['channel'])
                        
            elif result.get('job_status', None) == 'finished':
    
                #get all records concerned by this job
                records = database(jobname = result.get('job', None))
                
                if self._accepting_new and len(records) == 0:
                    now = datetime.datetime.utcnow()
                    # no dirmon message received so check in the waiting list and update it or add it in the waiting list if not present
                    database.insert(jobname = result.get('job', None), \
                                    finished = result['time'], \
                                    finished_time_insert = datetime.datetime.utcnow(), \
                                    created = now, \
                                    last_update= now, channel = result['channel'])
                    
                else:
                    for rec in records:
                        # update info with finished time
                        database.update(rec, finished = result['time'], \
                                        finished_time_insert = datetime.datetime.utcnow(), \
                                        last_update= datetime.datetime.utcnow(), channel = result['channel']) 
            else:
                
                Analyzer.LOG.debug("Ignored record = %s \n" % (result))
                
                # no status so it should be WRN or ERR
                self.warn_err_db.insert(lvl = result.get('lvl', None), \
                                        msg = result.get('msg', None), \
                                        created = datetime.datetime.utcnow())
                
                #Analyzer.LOG.info("Insert message in error or warn db %s" %(result))
         
                    
    def print_on_display(self, a_display, a_last_time_display):  #pylint: disable-msg=R0201
        """
           Display every x seconds
        """ 
        current_time = datetime.datetime.utcnow()
        if not a_last_time_display:
            a_display.print_screen(self.mem_db, current_time, self._sort_criteria)
            return current_time
        else:
            if current_time - a_last_time_display > datetime.timedelta(seconds=2):
                
                #clean database 
                self.remove_expired_records(self.mem_db)
                
                a_display.print_screen(self.mem_db, current_time, self._sort_criteria)
                return current_time
            else:
                return a_last_time_display
    
    def analyze_from_tailed_file(self, a_file_paths, a_go_to_the_end = True): #pylint: disable-msg=R0912
        """
           Analyze from an aggregated file containing xferlog, dirmon.log and send.log
        """
        files = []
        for f_path in a_file_paths:
            files.append(open(f_path, 'r'))
        
        f_iter = multitail.MultiFileTailer.tail(files, delay=0.4, go_to_the_end = a_go_to_the_end)
        
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
                    elif kb_input and kb_input == 'STOPACCEPTING':
                        Analyzer.LOG.error("*********** Stop Accepting")
                        self._accepting_new = False
                    elif kb_input and kb_input == 'RESTARTACCEPTING':
                        Analyzer.LOG.error("*********** Restart Accepting")
                        self._accepting_new = True
                    elif kb_input and kb_input == 'OLDEST':
                        Analyzer.LOG.error("*********** OLDEST records first")
                        self._sort_criteria = 'OLDEST'
                    elif kb_input and kb_input == 'NEWEST':
                        Analyzer.LOG.error("*********** NEWEST records first")
                        self._sort_criteria = 'NEWEST'
                        
            else:
                #force update
                self.print_on_display(self.mem_db, self.display, None)
                  
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
    
    log_utils.LoggerFactory.setup_simple_file_handler('/tmp/analyze.log', level = 3) 
    
    analyzer = Analyzer(enable_archive = False) #pylint: disable-msg=C0103
    
    #sys.exit(analyzer.analyze_with_text_display_from_tailed_file(['/tmp/res.txt']))

    #sys.exit(analyzer.analyze_from_tailed_file(['/tmp/analyse/logfile.log']))
    sys.exit(analyzer.analyze_from_tailed_file(['/tmp/analyse/xferlog_deleted.log'],a_go_to_the_end = False))
    