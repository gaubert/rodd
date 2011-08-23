'''
Created on Mar 10, 2011

@author: gaubert
'''
import os
import sys
import time
import datetime
import calendar
import csv

def compute_timeliness(a_file_start, a_file_end):
    """ compute the timeliness by relating filenames between 2 files """
    fd_s = open(a_file_start)
    
    csvWriter = csv.writer(open('/tmp/oscat_timeliness.csv', 'wb'), delimiter=',')
    csvWriter.writerow(['filename', 'timeliness (sec)', 'transfer rate (Kb/s)', 'size', 'start date', 'end date'])
    
    csvWriter_less = csv.writer(open('/tmp/oscat_timeliness_less_500KB.csv', 'wb'), delimiter=',')
    csvWriter_less.writerow(['filename', 'timeliness (sec)', 'transfer rate (Kb/s)', 'size', 'start date', 'end date'])
    
    csvWriter_more = csv.writer(open('/tmp/oscat_timeliness_more_500KB.csv', 'wb'), delimiter=',')
    csvWriter_more.writerow(['filename', 'timeliness (sec)', 'transfer rate (Kb/s)', 'size', 'start date', 'end date'])
    
    
    
    
    for line in fd_s:
        line_bits = line.split(' ')
       
        start_time  = line_bits[18]
        size        = line_bits[22]
        fname       = line_bits[23]
        fname       = os.path.basename(fname)[:-4]
       
        with open(a_file_end) as fd_e:
            for line in fd_e:
                if line.find(fname) != -1:
                    other_line_bits = line.split(' ')
                    end_time = other_line_bits[15][:-10]
                    #print("start_time = %s, end_time = %s, size = %s\n" % (start_time, end_time, size) )
                    t1 = time.strptime("2010-01-01T%s" % (start_time) ,"%Y-%m-%dT%H:%M:%S")
                    t1 = time.mktime(t1)
                    
                    t2 = time.strptime("2010-01-01T%s" % (end_time),"%Y-%m-%dT%H:%M:%S.%f")
                    t2 = time.mktime(t2)
                    
                    print("*** filename: %s" % (fname))
                    print("    time delta = %s, size = %s \n" %( (t2-t1), size))
                    print("***\n")
                    csvWriter.writerow([fname, (t2-t1), round( (float(size)/float(t2-t1))/1024 ,2), size, start_time, end_time])
                    
                    if int(size) > 500000:
                        csvWriter_more.writerow([fname, (t2-t1), round( (float(size)/float(t2-t1))/1024 ,2), size, start_time, end_time])
                    else:
                        csvWriter_less.writerow([fname, (t2-t1), round( (float(size)/float(t2-t1))/1024 ,2), size, start_time, end_time])
                  
                



if __name__ == '__main__':
    dir = "/homespace/gaubert/Data/OSCAT_TIMELINESS"
    f_start = "uplink_server.txt"
    f_end   = "workstation_reception.txt"
    compute_timeliness("%s/%s" % (dir, f_start), "%s/%s" % (dir, f_end))