'''
Created on Jan 19, 2010

@author: guillaume.aubert@ctbto.org
'''
import os
import sqlalchemy
import datetime
import calendar
import subprocess
import re

def makedirs(aPath):
    """ my own version of makedir """
    
    if os.path.isdir(aPath):
        # it already exists so return
        return
    elif os.path.isfile(aPath):
        raise OSError("a file with the same name as the desired dir, '%s', already exists."%(aPath))

    os.makedirs(aPath)

class MSGSYSExtractor(object):
    """
       This class extract data messages from the archive 
    """
    
    def __init__(self, a_ops_url, a_arch_url, a_export_dir):
        
        self._db_url   = a_ops_url
        self._arch_url = a_arch_url 
        
        self._export_dir = a_export_dir
        
        
        self._db_engine  = sqlalchemy.create_engine(self._db_url)
        self._db_conn    = self._db_engine.connect()
        
        self._arch_db_engine = sqlalchemy.create_engine(self._arch_url)
        self._arch_conn      = self._arch_db_engine.connect()
        
        makedirs(a_export_dir)
    
    def extract_request_and_subscription(self):
        """ raw method for extracting the request """
        
        #t = 'abcbcbcbc\nSTA_STATUS\nfffffff'
        #re_group_bull = re.compile('chan_status|sta_status',re.I)
        #res = re_group_bull.search(t) 
        
        re_group_bull = re.compile('chan_status|sta_status',re.I)
        #re_group_bull = re.compile('request',re.I)
        
        print('execute sql req\n')
        
        results = self._db_conn.execute("select * from idcx.msgdisc where msgtype in ('SUBSCRIPTION','REQUEST') and LDDATE < to_date('2008-07-08','YYYY-MM-DD HH24:MI:SS') order by LDDATE DESC")
        
        print('got the sql results\n')
        
        cpt = 1
        for row in results:
            
            the_dir       = row['DIR']
            the_file      = row['DFILE']
            the_s_off     = row['FILEOFF']
            the_file_size = row['FILESIZE']
            #what is that ?
            mf_off        = row['MFOFF']
            f_off         = row['FOFF']
            
            
            file_path = '%s/%s' % (the_dir, the_file)
            
            fd = open(file_path)
            
            print('read file %d %s' % (cpt,file_path))
            
            try:
                fd.seek(the_s_off)
                file_content = fd.read(the_file_size)
            except Exception, exce:
                print('ERROR when trying to read %s from offset %s, the exception %s\n' %(file_path,the_s_off,exce))
            
            if re_group_bull.search(file_content):
                print('found one matching file over %d total read files.' % (cpt))
                copy_fd = '%s/%s_%d' %(self._export_dir, the_file, cpt)
                copy_fd = open(copy_fd,'w')
                copy_fd.write(file_content)
                copy_fd.close()
            
            cpt += 1
        
        print('Parse %d total files' %(cpt))
    
    def extract_active_subscriptions(self):
        """ get active subscription """
        
        # get all valid subscription from subs
        results = self._db_conn.execute("select * from idcx.subs where status='a' order by lddate ")
        cpt = 1
        for row in results:
            
            msgid = row['INTID']
            
            # look in msg_id in obs_db and if not present look in the archive
            msgdisc_results = self._db_conn.execute("select * from idcx.msgdisc where msgid=%s" % (msgid) ).fetchall()
            
            #if nothing look in the archive
            if len(msgdisc_results) == 0:
                print("No subs into ops with msgid %s. Look in the archive" % (msgid) )
                msgdisc_results = self._arch_conn.execute("select * from idcx.msgdisc where msgid=%s" % (msgid) ).fetchall()
            
            if len(msgdisc_results) == 0:
                print("Cannot find msgdisc info for subscription with msgid %s" % (msgid) )
               
            for msg_row in msgdisc_results:
                
                the_dir       = msg_row['DIR']
                the_file      = msg_row['DFILE']
                the_s_off     = msg_row['FILEOFF']
                the_file_size = msg_row['FILESIZE']
                #what is that ?
                mf_off        = msg_row['MFOFF']
                f_off         = msg_row['FOFF']
                
                
                file_path = '%s/%s' % (the_dir, the_file)
                
                fd = open(file_path)
                
                print('read file %d %s' % (cpt,file_path))
                
                try:
                    fd.seek(the_s_off)
                    file_content = fd.read(the_file_size)
                except Exception, exce:
                    print('ERROR when trying to read %s from offset %s, the exception %s\n' %(file_path,the_s_off,exce))
                
                copy_fd = '%s/%s_%d' %(self._export_dir, the_file, cpt)
                copy_fd = open(copy_fd,'w')
                copy_fd.write(file_content)
                copy_fd.close()
                
            cpt += 1
        
        print('Parse %d total files' %(cpt))
    
    
            
            
if __name__ == "__main__":
    
    ops_db  = 'oracle://centre:data@odb.ctbto.org'
    
    arch_db = 'oracle://centre:data@adb.ctbto.org'
    
    msg_extractor = MSGSYSExtractor(ops_db, arch_db, '/tmp/active_subscription')
    
    msg_extractor.extract_active_subscriptions()