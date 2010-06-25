'''
Created on Sep 7, 2009

@author: guillaume.aubert@ctbto.org
'''

import os
import shutil
import sqlalchemy
import datetime
import calendar
import subprocess


def makedirs(aPath):
    """ my own version of makedir """
    
    if os.path.isdir(aPath):
        # it already exists so return
        return
    elif os.path.isfile(aPath):
        raise OSError("a file with the same name as the desired dir, '%s', already exists."%(aPath))

    os.makedirs(aPath)
    
def jday2datetime(a_jday_str):
    """
       convert jday (YYYY-DDD) in datetime
        
        Args:
            a_jday_str: the epoch time to convert
               
        Returns: a datetime
    """
    return datetime.datetime.strptime(a_jday_str,'%Y%j')

def datetime2e(a_date):
    """ 
        convert datetime in epoch
        Beware the datetime as to be in UTC otherwise you might have some surprises
            Args:
               a_date: the datertime to convert
               
            Returns: a epoch time
    """
    return calendar.timegm(a_date.timetuple())

class SHIDBExtractor(object):
    """
       This class extract data from the Archive and copies all necessary files
    """
    
    def __init__(self, a_ops_url, a_arch_url, a_export_dir):
        
        self._ops_db_url = a_ops_url
        self._arc_db_url = a_arch_url
        
        self._export_dir = a_export_dir
        
        
        self._ops_engine  = sqlalchemy.create_engine(self._ops_db_url)
        self._ops_conn    = self._ops_engine.connect()
        
        makedirs(a_export_dir)
        
    def _extract_from_table_as_spool(self, a_schema, a_table, a_request):
        """ use the horrible oracle spool mode """
        
        print("Extract %s.%s as spool file in %s\n" % (a_schema, a_table, self._export_dir) )
        
        cmd_file = "/tmp/cmd_file"
        
        f = open(cmd_file,"w")
        
        cmd = "/usr/lib/oracle/xe/app/oracle/product/10.2.0/server/bin/sqlplus centre/data@moorea.ctbto.org < %s" % (cmd_file)
        
        file_path = "%s/%s_%s.spool" % (self._export_dir, a_schema, a_table)
        
        the_spool_req = "set linesize 220;\nspool %s;\n%s;\n" % (file_path, a_request)
        
        f.write(the_spool_req)
        f.close()
        
        # Create output log file
        outFile = os.path.join(os.curdir, "/tmp/spool_cmd.out")
        outptr = file(outFile, "w")

        # Create error log file
        errFile = os.path.join(os.curdir, "/tmp/spool_cmd.err")
        errptr = file(errFile, "w")

        # Call the subprocess using convenience method
        
        print("cmd executed %s\nWith %s content\n %s\n===========" % (cmd, cmd, the_spool_req))
        
        
        retval = subprocess.call(cmd, shell=True, stdout = outptr, stderr= errptr)
        
        # Close log handles
        errptr.close()
        outptr.close()

        # Check the process exit code
        if not retval == 0:
            errptr = file(errFile, "r")
            errData = errptr.read()
            errptr.close()
            raise Exception("Error executing command: " + repr(errData))

        return 0
        
    
    def _extract_from_table_as_csv(self, a_schema, a_table, a_request):
        """ create csv file
        """
        
        print("Extract %s.%s as csv file in %s\n" % (a_schema, a_table, self._export_dir) )
        
        filename = "%s/%s_%s.csv" % (self._export_dir, a_schema, a_table)
        
        file_result = open(filename, "w")
        
        # run request
        results = self._ops_conn.execute(a_request)
        
        cpt = 0
        for row in results:
            line =""
            if cpt == 0:
                # first line create column
                i = 0
                for key in row.keys():
                    if i == 0:
                        line += "%s" % (key)
                    else:
                        line += ", %s" % (key)
                    i += 1
                
                file_result.write("%s \n" %(line))
                line =""
                
            i = 0
            for val in row.values():
                
                #print('type(val) = %s' %(type(val)))
                
                if i == 0:
                    line += "%s" % (val if type(val) != type('') else '"%s"' % (val))
                else:
                    line += ", %s"% (val if type(val) != type('') else '"%s"' % (val))
                
                i += 1
            
            file_result.write("%s \n" %(line))
            
            cpt += 1
        
        return 0
                
         
    def _extract_from_table_as_insert(self, a_schema, a_table, a_request):
        """
           create inserts files
        """
        
        filename = "%s/%s_%s.sql" % (self._export_dir, a_schema, a_table)
        
        print("Extract as insert file in %s\n" % (filename) )
        
        file_result = open(filename, "w")
        
        # run request
        print("Request to execute %s\n" %(a_request) )
        
        results = self._ops_conn.execute(a_request)
        
        columns = None
        
        # write intro
        file_result.write("WHENEVER SQLERROR EXIT SQL.SQLCODE;\n")
        
        file_result.write("alter session set NLS_DATE_FORMAT='YYYY-MM-DD HH24:MI:SS';\n")
        
        for row in results:
            
            # create columns in insert just once
            if not columns:
                i = 0
                columns = ""
                for key in row.keys():
                    if i == 0:
                        columns += "%s" %(key)
                    else:
                        columns += ", %s" %(key)
                    
                    i += 1
                    
                
            
            # collect values and create INSERT REQ
            i = 0
            values = ""
            for val in row.values():
                if i == 0:
                    values += "'%s'" % (val) if val else 'NULL'
                else:
                    values += ", '%s'" % (val) if val else ', NULL'
                i += 1
              
            insert_req = "INSERT into %s.%s (%s) values (%s);" % (a_schema, a_table, columns, values)
            #print("Generated req = %s \n" %(insert_req))
            file_result.write("%s\n" % (insert_req))
        
        file_result.write("commit ;\n")
        
        return 0
        

    def extract_from_table(self, a_schema, a_table, a_request, a_format='insert'):
        """
           extract from table. a_format can be 'insert', 'spool' or 'csv'
        """
        
        if a_format.lower() == 'insert':
            return self._extract_from_table_as_insert(a_schema, a_table, a_request)
        elif a_format.lower() == 'spool':
            return self._extract_from_table_as_spool(a_schema, a_table, a_request)
        elif a_format.lower() == 'csv':
            return self._extract_from_table_as_csv(a_schema, a_table, a_request)
    
    def extract_waveform_data_from_wavestore(self, a_schema, a_table, a_request):
        """
          destination directory
        """ 
       
        # run request
        print("Request to execute %s\n" %(a_request) )
         
        results = self._ops_conn.execute(a_request)
        
        for row in results:
            
            the_dir   = row['DIR']
            the_dfile = row['DFILE']
            
            src_file     = '%s/%s' % (the_dir, the_dfile)
            
            dest_dir = '%s/waveform_data/%s' % (self._export_dir, the_dir) 
            
            dest_file = '%s/%s' % (dest_dir, the_dfile)
            
            makedirs(dest_dir)
            
            #copy it only if it doesn't already exist
            if not os.path.exists(dest_file):
                print "Copy %s to %s" % (src_file, dest_file)
                shutil.copyfile(src_file, dest_file)
           
           
       
        
    
def extract_data_mining_berkely(a_begin_jday, a_end_jday):
    ''' extract tables for berkely data mining  project '''
    
    """
     => empty Idcx.detection
    Leb.amplitude => Done
    Leb.apma => Done
    Leb.arrival => Done
    Leb.detection => Done
    Reb.amplitude => Done
    Reb.apma => Done
    Reb.detection => Done
    Sel3.assoc => Done
    Sel3.origerr => Done
    Sel3.origin => Done
    Sitechan 
    """
   
    archive_db = 'oracle://centre:data@moorea.ctbto.org'
    
    ops_db     = 'oracle://centre:data@maui.ctbto.org'
    
    #datetime.datetime.strptime(a_begin_jday,'%Y%j')
    
    # convert date in epoch
    begin    = jday2datetime(a_begin_jday)
    end      = jday2datetime(a_end_jday)
    
    e_beg    = datetime2e(begin)-10
    e_end    = datetime2e(end)+10
    
    print("begin = %s\n" % (begin))
    print("end = %s\n" % (end))
   
   
    extractor = SHIDBExtractor(archive_db, archive_db,'/tmp/data/2009081-2009171-csv-v1.3')
   
    format = 'csv'
   
    
    
    #arrival req
    arrival_req = "select %s from %s.arrival where time between %s and %s"
    
    #orig_req
    orig_req = "select %s from %s.origin where time between %s and %s"
    
    
    schema = 'static'
    
    #sitechan
    extractor.extract_from_table(schema, "sitechan", "select * from %s.sitechan" % (schema), format)
    
    extractor.extract_from_table(schema, "site", "select * from %s.site" % (schema), format)
    
    extractor.extract_from_table(schema, "affiliation", "select * from %s.affiliation" % (schema), format)
    
    schema = 'idcx'
    
    extractor.extract_from_table(schema, "wfdisc", "select * from %s.wfdisc where time between %s and %s" % (schema, e_beg, e_end), format)
    
    #idcx_amplitude
    extractor.extract_from_table(schema, "amplitude", "select * from %s.amplitude amp where amp.arid in (%s)" % (schema, arrival_req % ('arid', schema, e_beg, e_end)), format)
    
    # idcx apma
    extractor.extract_from_table(schema, "apma", "select * from %s.apma apma where apma.arid in (%s)" % (schema, arrival_req % ('arid', schema, e_beg, e_end)), format)
    
    # idcx apma
    extractor.extract_from_table(schema, "arrival", "select %s from %s.arrival where time between %s and %s" % ('*', schema, e_beg, e_end), format)
    
    #detection
    extractor.extract_from_table(schema, "detection", "select * from %s.detection where time between %s and %s" % (schema, e_beg, e_end), format)
    
    # LEB Data
    schema = 'leb'
    
    # get amp3c from arrival 
    extractor.extract_from_table(schema, "amp3c", "select amp3c.* from %s.amp3c amp3c, %s.arrival arr where amp3c.arid = arr.arid and arr.time between %s and %s" % (schema, schema,  e_beg, e_end), format)

    # get amplitude from arrival
    extractor.extract_from_table(schema, "amplitude", "select * from %s.amplitude where arid in (%s)" % (schema, arrival_req % ('arid', schema, e_beg, e_end)), format)

    # get apma from arrival
    extractor.extract_from_table(schema, "apma", "select apma.* from %s.apma apma, %s.arrival arr where apma.arid = arr.arid and arr.time between %s and %s" % (schema, schema, e_beg, e_end), format)

    # get arrival for leb
    extractor.extract_from_table(schema, "arrival", arrival_req % ('*', schema, e_beg, e_end), format )
    
    # get assoc
    extractor.extract_from_table(schema, "assoc", "select * from %s.assoc where orid in (%s)" % (schema,orig_req % ('orid', schema, e_beg, e_end)), format)
    
    #detection
    extractor.extract_from_table(schema, "detection", "select * from %s.detection where time between %s and %s" % (schema, e_beg, e_end), format)
    
    # get discard 
    extractor.extract_from_table(schema, "discard", "select * from %s.discard where evid in (%s)" % (schema, orig_req % ('distinct evid', 'sel3', e_beg, e_end)), format)
   
    # get discard 
    extractor.extract_from_table(schema, "origerr", "select * from %s.origerr where orid in (%s)" % (schema, orig_req % ('distinct orid', schema, e_beg, e_end)), format)
    
    # get origin 
    extractor.extract_from_table(schema, "origin", orig_req % ('*', schema, e_beg, e_end), format)
    
    # Reb Data
    # amplitude
    schema = 'reb'
    
    # get amp3c from arrival 
    extractor.extract_from_table(schema, "amp3c", "select amp3c.* from %s.amp3c amp3c, %s.arrival arr where amp3c.arid = arr.arid and arr.time between %s and %s" % (schema, schema,  e_beg, e_end), format)

    # get amplitude from arrival
    extractor.extract_from_table(schema, "amplitude", "select * from %s.amplitude where arid in (%s)" % (schema, arrival_req % ('arid', schema, e_beg, e_end)), format)

    # get apma from arrival
    extractor.extract_from_table(schema, "apma", "select apma.* from %s.apma apma, %s.arrival arr where apma.arid = arr.arid and arr.time between %s and %s" % (schema, schema, e_beg, e_end), format)

    # get arrival for leb
    extractor.extract_from_table(schema, "arrival", arrival_req % ('*', schema, e_beg, e_end), format )
    
    # get assoc
    extractor.extract_from_table(schema, "assoc", "select * from %s.assoc where orid in (%s)" % (schema,orig_req % ('orid', schema, e_beg, e_end)), format)
    
    #detection
    extractor.extract_from_table(schema, "detection", "select * from %s.detection where time between %s and %s" % (schema, e_beg, e_end), format)
    
    # get discard 
    extractor.extract_from_table(schema, "discard", "select * from %s.discard where evid in (%s)" % (schema, orig_req % ('distinct evid', 'sel3', e_beg, e_end)), format)
    #extractor.extract_from_table(schema, "discard", "select * from %s.discard where lddate between to_date ('%s','YYYY-MM-DD HH24:MI:SS') and to_date ('%s','YYYY-MM-DD HH24:MI:SS')" % (schema,begin, end), format)
    
    
    # get origerr 
    extractor.extract_from_table(schema, "origerr", "select * from %s.origerr where orid in (%s)" % (schema, orig_req % ('distinct orid', schema, e_beg, e_end)), format)
    
    # get origin 
    extractor.extract_from_table(schema, "origin", orig_req % ('*', schema, e_beg, e_end), format)
    
    # sel3 data
    schema = 'sel3'
    
    # get assoc
    extractor.extract_from_table(schema, "assoc", "select * from %s.assoc where orid in (%s)" % (schema,orig_req % ('orid', schema, e_beg, e_end)), format)
    
    # get orig
    extractor.extract_from_table(schema, "origin", orig_req % ('*', schema, e_beg, e_end), format)
    
    #get origerr
    extractor.extract_from_table(schema, "origerr", "select * from %s.origerr where orid in (%s) " % (schema, orig_req % ('orid', schema, e_beg, e_end)), format )
    


def nms_project():
    
    archive_db = 'oracle://centre:data@moorea.ctbto.org'
    ops_db     = 'oracle://centre:data@maui.ctbto.org'

    schema     = "LEB"

    extractor = SHIDBExtractor(ops_db, archive_db,'/tmp/data/leb')
    
    orig_req = "select %s from %s.origin where time between 1245542400 and 1245600000"
    
    extractor.extract_from_table(schema, "ORIGIN", orig_req % ('*', schema))
    
    extractor.extract_from_table(schema, "ORIGERR", "select * from %s.origerr where orid in (%s) " % (schema, orig_req % ('orid', schema)) )
    
    extractor.extract_from_table(schema, "ASSOC", "select * from %s.assoc where orid in (%s) " % (schema, orig_req % ('orid', schema)) )
    
    extractor.extract_from_table(schema, "STAMAG", "select * from %s.stamag where orid in (%s) " % (schema, orig_req % ('orid', schema)))
    
    extractor.extract_from_table(schema, "NETMAG", "select * from %s.netmag where orid in (%s) " % (schema, orig_req % ('orid', schema)) )
    
    #extractor.extract_from_table("REB", "EVENT", "select * from %s.event where evid in (%s) " % (orig_req % ('distinct evid'), schema) )
    
    extractor.extract_from_table(schema, "STAMAG", "select * from %s.stamag where orid in (%s) " % (schema, orig_req % ('orid', schema)))
    
    # Arrival
    arrival_req = "select %s from %s.arrival where time between 1245542400-1 and 1245600000+1"
    
    extractor.extract_from_table(schema, "ARRIVAL", arrival_req % ('*', schema) )
    
    extractor.extract_from_table(schema, "AMPLITUDE", "select * from %s.amplitude where arid in (%s)" % (schema, arrival_req % ('arid', schema)) )
    
    #extractor.extract_from_table("STATIC", "GREGION", "select * from static.gregion")

def nms_evscr_data_set():
    """ extract the event screening info """
    
    start      = '1245542400' # 21 june 2008
    end        = '1245600000' # 22 june 2008
    
    archive_db = 'oracle://centre:data@adb.ctbto.org'
    ops_db     = 'oracle://centre:data@odb.ctbto.org'
    
    schema    = 'IDCX'
    
    extractor = SHIDBExtractor(archive_db, archive_db,'/tmp/data/shi_archive')
    
    orig_req = "select %s from %s.origin where" + " time between %s and %s" % (start, end)
    
    #get static table
    extractor.extract_from_table(schema, "PRODUCTTYPEEVSC", "select * from %s.producttypeevsc" % (schema) )
    
    extractor.extract_from_table(schema, "EVSC_PROD", "select * from %s.evsc_prod where orid in (%s) " \
                                 % (schema, orig_req % ('orid', 'REB')) )
    
    extractor.extract_from_table(schema, "EVSC_HYDRO", "select * from %s.evsc_hydro where orid in (%s) " \
                                 % (schema, orig_req % ('orid', 'REB')) )
    
    extractor.extract_from_table(schema, "EVSC_REGIONAL", "select * from %s.evsc_regional where orid in (%s) " \
                                 % (schema, orig_req % ('orid', 'REB')) )
    



def nms_project_get_waveform_set():
    
    archive_db = 'oracle://centre:data@adb.ctbto.org'
    #look into the archive
    ops_db = archive_db
    #ops_db     = 'oracle://centre:data@odb.ctbto.org'

    schema    = 'IDCX'
    
    start      = '1245542400' # 18 Jan 2008 00:00:00
    end        = '1245546000' # 18 Jan 2008 01:00:00
    
    req = "select * from idcx.wfdisc where time between 1245542400 and 1245546000 and (STA like 'AR%' or STA like 'GE%' or STA like 'I22%' or STA like 'H08N%' or STA like 'H08S%' or STA like 'H10N%' or STA like 'H10S%' or STA like 'MK%' or STA like 'TO%' or STA like 'TX%' or STA like 'W%')"
    
    extractor = SHIDBExtractor(ops_db, archive_db,'/tmp/data/nms_wavestore')
    
    extractor.extract_from_table(schema, "WFDISC", req )
    
    extractor.extract_waveform_data_from_wavestore(schema, "WFDISC", req)
    
    

def nms_project_archive_data_set():
    
    archive_db = 'oracle://centre:data@adb.ctbto.org'
    #look into the archive
    ops_db = archive_db
    #ops_db     = 'oracle://centre:data@odb.ctbto.org'

    schemas    = ['SEL1','SEL2','SEL3', 'LEB','REB']
    
    start      = '1200614400' # 18 Jan 2008 00:00:00
    end        = '1200700800' # 19 Jan 2008 00:00:00
    
    extractor = SHIDBExtractor(ops_db, archive_db,'/tmp/data/shi_archive')
    
    arrival_idcx_done = False
    
    for schema in schemas:
        
        orig_req = "select %s from %s.origin where" + " time between %s and %s" % (start, end)
    
        extractor.extract_from_table(schema, "ORIGIN", orig_req % ('*', schema))
    
        extractor.extract_from_table(schema, "ORIGERR", "select * from %s.origerr where orid in (%s) " \
                                     % (schema, orig_req % ('orid', schema)) )
    
        extractor.extract_from_table(schema, "ASSOC", "select * from %s.assoc where orid in (%s) " \
                                     % (schema, orig_req % ('orid', schema)) )
    
        extractor.extract_from_table(schema, "STAMAG", "select * from %s.stamag where orid in (%s) " \
                                     % (schema, orig_req % ('orid', schema)))
    
        extractor.extract_from_table(schema, "NETMAG", "select * from %s.netmag where orid in (%s) " \
                                     % (schema, orig_req % ('orid', schema)) )
    
        extractor.extract_from_table(schema, "EVENT", "select * from %s.event where evid in (%s) " \
                                     % (schema, orig_req % ('distinct evid', schema) ) ) 
        
        arrival_req = "select %s from %s.arrival where" + " time between %s-1 and %s+1" % (start, end)
        
        # get arrival table for leb and reb
        if schema in ('LEB', 'REB'):
            # Arrival
            extractor.extract_from_table(schema, "ARRIVAL", arrival_req % ('*', schema) )
            
            extractor.extract_from_table(schema, "AMPLITUDE", "select * from %s.amplitude where arid in (%s)" % (schema, arrival_req % ('arid', schema)) )
            
        else:
            if not arrival_idcx_done:
                extractor.extract_from_table('IDCX', "ARRIVAL", arrival_req % ('*', schema) )
            
                extractor.extract_from_table('IDCX', "AMPLITUDE", "select * from %s.amplitude where arid in (%s)" % (schema, arrival_req % ('arid', schema)) ) 
            
                arrival_idcx_done = True
                
def vdec_project_get_waveform_data_set():
    
    archive_db = 'oracle://centre:data@adb.ctbto.org'
    #look into the archive
    ops_db = archive_db
    #ops_db     = 'oracle://centre:data@odb.ctbto.org'
    
    start      = '1207008000' # 01 Apr 2008 00:00:00 
    end        = '1246406400' # 01 Jul 2009 00:00:00
    
    req = "select * from idcx.wfdisc where time between %s and %s order by time" % (start, end)
    
    extractor = SHIDBExtractor(ops_db, archive_db,'/tmp/data/vdec_data_set_01Apr08-01Jul09')
    
    extractor.extract_from_table("IDCX", "WFDISC", req )
    
    

def vdec_project_data_set():
    
    archive_db = 'oracle://centre:data@adb.ctbto.org'
    #look into the archive
    ops_db = archive_db
    #ops_db     = 'oracle://centre:data@odb.ctbto.org'

    schemas    = ['SEL1','SEL2','SEL3','LEB','REB']
    
    start      = '1207008000' # 01 Apr 2008 00:00:00 
    end        = '1246406400' # 01 Jul 2009 00:00:00
    
    extractor = SHIDBExtractor(ops_db, archive_db,'/tmp/data/vdec_data_set_01Apr08-01Jul09')
    
    arrival_idcx_done = False
    
    for schema in schemas:
        
        #the orig req
        orig_req = "select %s from %s.origin where" + " time between %s and %s" % (start, end)
        
        # request based on arids
        arrival_req = "select %s from %s.arrival where" + " time between %s-1 and %s+1" % (start, end)
        
        # get arrival table for leb and reb
        if schema in ('LEB', 'REB'):
            # Arrival
            #extractor.extract_from_table(schema, "ARRIVAL", arrival_req % ('*', schema) )
            
            extractor.extract_from_table(schema, "AMPLITUDE", "select * from %s.amplitude where arid in (%s)" % (schema, arrival_req % ('arid', schema)) )
            
            # idcx apma
            #extractor.extract_from_table(schema, "APMA", "select * from %s.apma apma where apma.arid in (%s)" % (schema, arrival_req % ('arid', schema)))
    
            #detection
            #extractor.extract_from_table(schema, "DETECTION", "select * from %s.detection where time between %s and %s" % (schema, start, end))
            
            #extractor.extract_from_table(schema, "discard", "select * from %s.discard where evid in (%s)" % (schema, orig_req % ('distinct evid', 'sel3')))
        
            print 'do nothing'
        else:
            if not arrival_idcx_done:
                #extractor.extract_from_table('IDCX', "ARRIVAL", arrival_req % ('*', schema) )
            
                extractor.extract_from_table('IDCX', "AMPLITUDE", "select * from %s.amplitude where arid in (%s)" % (schema, arrival_req % ('arid', schema)) ) 
                
                # idcx apma
                #extractor.extract_from_table('IDCX', "APMA", "select * from %s.apma apma where apma.arid in (%s)" % (schema, arrival_req % ('arid', schema)))
    
                #detection
                #extractor.extract_from_table('IDCX', "DETECTION", "select * from %s.detection where time between %s and %s" % (schema, start, end))
            
                arrival_idcx_done = True
        
        # rest of the requests based on orig
    
        #extractor.extract_from_table(schema, "ORIGIN", orig_req % ('*', schema))
    
        #extractor.extract_from_table(schema, "ORIGERR", "select * from %s.origerr where orid in (%s) " % (schema, orig_req % ('orid', schema)) )
    
        #extractor.extract_from_table(schema, "ASSOC", "select * from %s.assoc where orid in (%s) " % (schema, orig_req % ('orid', schema)) )
    
        #extractor.extract_from_table(schema, "STAMAG", "select * from %s.stamag where orid in (%s) " % (schema, orig_req % ('orid', schema)))
    
        #extractor.extract_from_table(schema, "NETMAG", "select * from %s.netmag where orid in (%s) " % (schema, orig_req % ('orid', schema)) )
    
        #extractor.extract_from_table(schema, "EVENT", "select * from %s.event where evid in (%s) " % (schema, orig_req % ('distinct evid', schema) ) ) 

if __name__ == "__main__":
    
    vdec_project_get_waveform_data_set()
    #nms_project_get_waveform_set()
    #vdec_project_data_set()
    #nms_project()
    #nms_evscr_data_set()
    #nms_project_archive_data_set()
    
    #extract_data_mining_berkely('2009081' , '2009171')