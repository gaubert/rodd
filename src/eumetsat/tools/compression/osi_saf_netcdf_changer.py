'''
Created on Dec 2, 2010

@author: gaubert
'''

from netCDF4 import Dataset
import numpy
import subprocess
import sys
import fileinput
import tempfile
import os
import csv

import eumetsat.common.utils
from eumetsat.common.utils import ftimer

import ftplib

SERVER    = 'podaac.jpl.nasa.gov'
DIRECTORY = '/GHRSST2/data/L2P/AVHRR_METOP_A/EUR/2010/340'
FILES     = '*.bz2'

def list_ftp_dir(server, dir, files):
    """ return a list of files from a ftp dir """
    
    print("== list %s on %s\n" % (dir, server))
    
    ftp = ftplib.FTP(server)
    ftp.login()
    ftp.cwd(dir)
    
    res = ftp.nlst(files)
    
    return res

def download_file(server, dir, in_file, out_filename):
    """ download a file """
    
    print("== Get file %s in %s\n" % (in_file, out_filename))
    
    ftp = ftplib.FTP(server)
    ftp.login()
    ftp.cwd(dir)
    
    result_file = open(out_filename,"wb")
    ftp.retrbinary('RETR %s' %(in_file) , result_file.write)
    
    result_file.close()
    
    print("== End of Get file %s\n" % (in_file))

    

def generate_template_from_src(a_working_dir, a_input, a_output):
    """ generate cdl for original nc file and modify the lat lon type to be in the new type """
    
    create_cdl_script = "/homespace/gaubert/ecli-workspace/rodd/etc/compression/create_cdl.sh"
    
    print("== Create cdl %s/temp.cdl\n" %(a_working_dir))
    
    cdl_file = "%s/temp.cdl" % (a_working_dir)
    res = subprocess.call([create_cdl_script, a_input, cdl_file])
    
    if res != 0:
        print("Error: Problem while creating cdl %s file from %s" % (cdl_file, a_input))
    
    print("== Change types in %s/temp.cdl\n" %(a_working_dir))
    
    # replace all occurrences of 'sit' with 'SIT' and insert a line after the 5th
    for line in fileinput.input(cdl_file, inplace = 1):
        
        if line.find('float lat') >=0:  #change lat type
            line = line.replace('float lat', 'int lat')
        
        if line.find('float lon') >=0:  #change lon type
            line = line.replace('float lon', 'int lon')
        
        if line.find('lon:units = "degrees_east" ;') >=0:  #add extra params
            line += '        lon:scale_factor = 0.01 ;\n'
        
        if line.find('lat:units = "degrees_north" ;') >= 0: #add extra params
            line += '        lat:scale_factor = 0.01 ;\n'
        
        sys.stdout.write(line)
    
    print("== Generate new nc file %s/%s\n" % (a_working_dir,a_output) )
    #now create the nc file
    create_nc_script = "/homespace/gaubert/ecli-workspace/rodd/etc/compression/generate_nc_file.sh"
    res = subprocess.call([create_nc_script, cdl_file, "%s/%s" % (a_working_dir,a_output) ])
    
    if res != 0:
        print("Error: Problem while creating nc %s file from %s" % (create_nc_script))
        
    return "%s/%s" % (a_working_dir,a_output)
       


def transform_osi_saf_netcdf(new_data_set, digits, debug = False):
    """ Transform osi saf int netcdf """
    
    print("================== Start transforming netCDF coordinates (precision %s) ==================" % (digits) )
    
    
    old_dataset = Dataset('/homespace/gaubert/sstmgr/file.nc')
    
    new_dataset = Dataset(new_data_set,'a')

    o_lat = old_dataset.variables['lat']
    o_lon = old_dataset.variables['lon']
    
    o_lat_data = o_lat[:]
    o_lon_data = o_lon[:]
  
    #need to create a numpy array with the right dimensions and fill it with the scale lat values
    # and then the lon values
    n_data = numpy.zeros((1080,2048), dtype=int)
    
    nj_max = 1080
    ni_max = 2048
    
    nj = 0
    ni = 0
    print("== Start lat transformation \n")
    while nj < nj_max:
        while ni < ni_max:
            n_data[nj][ni] = round(o_lat_data[nj][ni], digits)*pow(10,digits)
            ni += 1
        
        if debug and (nj % 10) == 0:
            print("debug: In nj loop %d\n" % (nj))
        ni = 0
        nj += 1

    print("== End of lat transformation \n")
    
    new_dataset.variables['lat'][:]  = n_data
    new_dataset.sync()
    
    print("== Start lon transformation \n")
    n_data = numpy.zeros((1080, 2048), dtype=int)
    
    #reset ni nj
    ni = 0
    nj = 0
    
    while nj < nj_max:
        while ni < ni_max:
            n_data[nj][ni] = round(o_lon_data[nj][ni], digits)*pow(10,digits)
            ni += 1
        
        if debug and (nj % 10) == 0:
            print("debug: In nj loop %d\n" % (nj))
        ni = 0
        nj += 1

    print("== End of lon transformation \n")
    
    new_dataset.variables['lon'][:]  = n_data
    new_dataset.sync()
    

    new_dataset.close()
    
    old_dataset.close()
    
    print("================== End of transforming netCDF coordinates ==================")

def compress_files(original_filename, new_data_set, digits):
    """ compress the output file and gets its compressed size """
    
    print("== Start Compression tests for %s \n" %(new_data_set))
    
    # get data_set uncompressed size
    size = os.path.getsize(new_data_set)
    
    bzip2_script = "/homespace/gaubert/ecli-workspace/rodd/etc/compression/bzip2_compression.sh"
    
    func = subprocess.call
    
    res = []
            
    time_bzip2 = ftimer(func,[[bzip2_script, new_data_set, "%s.bz2" % (new_data_set) ] ], {}, res, number=1)

    print("\nTime: %s secs \n bzip2 file %s\n"%(time_bzip2 , new_data_set))

    if res[0] != 0:
        print("Error. Cannot bzip2 file %s" % (new_data_set))
       
    szip_script = "/homespace/gaubert/ecli-workspace/rodd/etc/compression/szip_compression.sh"
    
    time_szip = ftimer(func,[ [ szip_script, new_data_set, "%s.sz" % (new_data_set)  ] ], {}, res,number=1)

    print("\nTime: %s secs \n szip file %s\n" % (time_szip , new_data_set))

    if res[0] != 0:
        print("Error. Cannot bzip2 file %s" % (new_data_set))
       
    size_bzip2 = os.path.getsize("%s.bz2" %(new_data_set))
    
    size_szip  = os.path.getsize("%s.sz" %(new_data_set))
    
    print("bzip2 size %d. szip size %d" % (size_bzip2, size_szip))
    
    #return [( round(float(size)/float(size_bzip2), 2), size_bzip2, time_bzip2 ),( round(float(size)/float(size_szip), 2), size_szip, time_szip )]
    
    return {
            'name'  : os.path.basename(original_filename),
            '%d d bz2 size' % (digits) : size_bzip2, 
            '%d d bz2 ratio' % (digits) : round(float(size)/float(size_bzip2), 2), 
            '%d d bz2 compression time' % (digits) : round(time_bzip2,2),
            '%d d sz size' % (digits) : size_szip, 
            '%d d sz ratio' % (digits) : round(float(size)/float(size_szip), 2),
            '%d d sz compression time' % (digits): round(time_szip,2)
           }

def run_tests(filename, temp_root_dir, to_clean):
    """ run 2 digits and 3 digits precisons test for each files """

    bunzip2_script = "/homespace/gaubert/ecli-workspace/rodd/etc/compression/bunzip2.sh"
    
    tempdir = tempfile.mkdtemp(dir=temp_root_dir)
    
    output_download_file = '%s/%s' % (tempdir, filename)
    
    download_file(SERVER, DIRECTORY, filename, output_download_file)
    
    if output_download_file.endswith('.bz2'):
        res = subprocess.call([bunzip2_script, output_download_file])
        if res != 0:
            raise Exception("Error while uncompressing %s\n" % (output_download_file) )
        else:
            output_download_file = output_download_file[:-4]
            
    #test with 2 digits
    digits = 2
    
    output_file = generate_template_from_src(tempdir, output_download_file,'new-file.nc')

    transform_osi_saf_netcdf(output_file, digits)
    
    d1 = compress_files(output_download_file, output_file, digits)
    
    digits = 3
    
    transform_osi_saf_netcdf(output_file, digits)
    
    d2 = compress_files(output_download_file, output_file, digits)
    
    
    # clean temp dir
    if to_clean:
        eumetsat.common.utils.delete_all_under(tempdir, True)
    
    return dict(d1.items() + d2.items())



if __name__ == '__main__':
    
    TO_CLEAN      = True
    #ROOT_TEMP_DIR = "/homespace/gaubert/tempo"
    ROOT_TEMP_DIR = "/tmp/comp-tempo"
    
    if TO_CLEAN:
        #clean root dir
        eumetsat.common.utils.delete_all_under(ROOT_TEMP_DIR)
    
    #create csv file
    digits = 2
    
    fieldnames = ['%d d bz2 size'  % (digits) , '%d d bz2 ratio'  % (digits) , '%d d bz2 compression time'  % (digits) , '%d d sz size'  % (digits) , '%d d sz ratio'  % (digits) , '%d d sz compression time'  % (digits)]
    
    digits = 3
    fieldnames.extend(['%d d bz2 size'  % (digits) , '%d d bz2 ratio'  % (digits) , '%d d bz2 compression time'  % (digits) , '%d d sz size'  % (digits) , '%d d sz ratio'  % (digits) , '%d d sz compression time'  % (digits), 'name'  ])
   
    result_file = open('/tmp/result.csv', 'wb')
    writer = csv.DictWriter(result_file, fieldnames=fieldnames)
    headers = dict( (n,n) for n in fieldnames )
    writer.writerow(headers)
    
    result_file.flush()
    #result_file.close()

    list_of_files = list_ftp_dir(SERVER, DIRECTORY, FILES)
    
    icpt = 0
    for (i,the_file) in enumerate(list_of_files):
        
        print("####################### Run %d #######################\n" % (i))
        result_row = run_tests(the_file, ROOT_TEMP_DIR, TO_CLEAN)
        print("result_row = %s\n" %(result_row))
        writer.writerow(result_row)
        result_file.flush()
        icpt+=1
        if icpt == 100:
            break
    
    #transform_osi_saf_short_netcdf(output_file)