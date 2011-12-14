'''
Created on Dec 2, 2011

@author: guillaume.aubert@eumetsat.int
'''

import datetime
import eumetsat.dmon.common.log_utils  as log_utils
import eumetsat.dmon.common.time_utils  as time_utils

LOG = log_utils.LoggerFactory.get_logger('analyze_utils')

def print_rec_in_logfile(rec):
    """
       Print rec in file
    """
    LOG.info('*********** Delete fn=%s, jn=%s, cr=%s, up=%s,an=%s,bl=%s,lupdate=%s' % ( rec['filename'], rec['jobname'], \
                                                                                        time_utils.datetime_to_time(rec['created']), \
                                                                                        time_utils.datetime_to_time(rec['uplinked']), \
                                                                                        time_utils.datetime_to_time(rec['announced']), \
                                                                                        time_utils.datetime_to_time(rec['blocked']), \
                                                                                        time_utils.datetime_to_time(rec['last_update'])) )

def print_db_logfile(database): #pylint: disable-msg=R0201
    """
      print database in log file for debuging purposes
    """
    LOG.info('--BEG-------------------------------------------------------------------------')
    for rec in database:
        LOG.info('fn=%s, jn=%s, cr=%s, up=%s,an=%s,bl=%s,lupdate=%s' % ( rec['filename'], rec['jobname'], \
                                                                        time_utils.datetime_to_time(rec['created']), \
                                                                        time_utils.datetime_to_time(rec['uplinked']), \
                                                                        time_utils.datetime_to_time(rec['announced']), \
                                                                        time_utils.datetime_to_time(rec['blocked']), \
                                                                        time_utils.datetime_to_time(rec['last_update'])) )
    LOG.info('--END-------------------------------------------------------------------------')    
    


def db_differ(prev_snapshot, database):
    """
       return nb of deleted and already existing and new records
    """
    new_snapshot = {}
    existing = 0  #already existing
    new      = 0  # newly created 
    finished = 0  #newly finished
    
    for rec in database:
        ind = rec['__id__']
        if ind in prev_snapshot:
            existing += 1
            
            #check if it was already finished
            if rec.get('finished', None) and not prev_snapshot[ind].get('finished', None):
                finished += 1
            
            del prev_snapshot[ind]
            new_snapshot[ind] = rec
        else:
            
            if rec.get('finished', None):
                finished += 1
            
            new += 1
            new_snapshot[ind] = rec
    
    #get the deleted this is what is left in prev_snapshot
    deleted = len(prev_snapshot)
    
    return new_snapshot, deleted, new, existing, finished


def get_active_jobs(database, prev_snapshot, active_for_secs = 120):
    """
       Get the number of active jobs
    """
    finished    = 0
    blocked     = 0
    active      = 0
    
    active_for = {}
    
    results = {}
    
    for rec in database:
        if rec.get('finished_time_insert', None):
            finished += 1
        else:
            active += 1
            now = datetime.datetime.now()
            if now - rec.get('created') > datetime.timedelta(seconds = active_for_secs):
                #CurseDisplay.LOG.info("One active for more than %d secs" %(secs))
                active_for[rec['__id__']] = rec
                
        
        if rec.get('blocked', None) and not rec.get('finished', None):
            blocked += 1
        
    job_nb = 0    
    for j in database._jobname:
        if j is not None:
            job_nb += 1
        
    
    #active = len(database)- finished
    
    results['active_file_transfers']   = active
    results['finished_file_transfers'] = finished
    results['blocked_file_transfers']  = blocked
    results['total_nb_of_transfers']   = len(database)
    results['nb_active_for_x_secs']    = len(active_for)
    results['nb_jobs']                 = job_nb
 
    prev_snapshot, d_del, d_new, d_already_existing, d_finished = db_differ(prev_snapshot, database)
    
    results['since_last_print'] = {}
    results['since_last_print']['prev_snapshot'] = prev_snapshot
    results['since_last_print']['deleted']  = d_del
    results['since_last_print']['new']      = d_new
    results['since_last_print']['existing'] = d_already_existing
    results['since_last_print']['finished'] = d_finished
    
    
    return results