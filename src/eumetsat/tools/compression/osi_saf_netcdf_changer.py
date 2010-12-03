'''
Created on Dec 2, 2010

@author: gaubert
'''

from netCDF4 import Dataset
import numpy
import subprocess


def generate_template_from_src(a_filename):
    """ generate cdl file and modify the lat lon type to be in the new type """
    
    script = "/homespace/gaubert/ecli-workspace/rodd/etc/compression/create_cdl.sh"
    res = subprocess.call([script, a_filename])




def transform_osi_saf_int_netcdf():
    """ Transform osi saf int netcdf """
    
    old_dataset = Dataset('/homespace/gaubert/sstmgr/file.nc')
    
    new_dataset = Dataset('/homespace/gaubert/sstmgr/new-int_file.nc','a')

    o_lat = old_dataset.variables['lat']
    o_lon = old_dataset.variables['lon']
    
    o_lat_data = o_lat[:]
    o_lon_data = o_lon[:]
  
    #need to create a numpy array with the right dimensions and fill it with the scale lat values
    # and then the lon values
    n_data = numpy.zeros((1080,2048),dtype=int)
    
    nj_max = 1080
    ni_max = 2048
    
    nj = 0
    ni = 0
    print("Start lat transformation \n")
    while nj < nj_max:
        while ni < ni_max:
            n_data[nj][ni] = round(o_lat_data[nj][ni], 4)*10000 
            ni += 1
        
        if (nj % 10) == 0:
            print("in nj loop %d\n" % (nj))
        ni = 0
        nj += 1

    print("End of lat transformation \n")
    
    new_dataset.variables['lat'][:]  = n_data
    new_dataset.sync()
    
    print("Start lon transformation \n")
    n_data = numpy.zeros((1080,2048),dtype=int)
    
    #reset ni nj
    ni = 0
    nj = 0
    
    while nj < nj_max:
        while ni < ni_max:
            n_data[nj][ni] = round(o_lon_data[nj][ni], 2)*100 
            ni += 1
        
        if (nj % 10) == 0:
            print("in nj loop %d\n" % (nj))
        ni = 0
        nj += 1

    print("End of lon transformation \n")
    
    new_dataset.variables['lon'][:]  = n_data
    new_dataset.sync()
    

    new_dataset.close()
    
    old_dataset.close()


def transform_osi_saf_netcdf():
    """ Transform osi saf netcdf """
    
    old_dataset = Dataset('/homespace/gaubert/sstmgr/file.nc')
    
    new_dataset = Dataset('/homespace/gaubert/sstmgr/new-file.nc','a')

    o_lat = old_dataset.variables['lat']
    o_lon = old_dataset.variables['lon']
    
    o_lat_data = o_lat[:]
    o_lon_data = o_lon[:]
  
    #need to create a numpy array with the right dimensions and fill it with the scale lat values
    # and then the lon values
    n_data = numpy.zeros((1080,2048),dtype=int)
    
    nj_max = 1080
    ni_max = 2048
    
    nj = 0
    ni = 0
    print("Start lat transformation \n")
    while nj < nj_max:
        while ni < ni_max:
            n_data[nj][ni] = round(o_lat_data[nj][ni], 2)*100 
            ni += 1
        
        if (nj % 10) == 0:
            print("in nj loop %d\n" % (nj))
        ni = 0
        nj += 1

    print("End of lat transformation \n")
    
    new_dataset.variables['lat'][:]  = n_data
    new_dataset.sync()
    
    print("Start lon transformation \n")
    n_data = numpy.zeros((1080,2048),dtype=int)
    
    #reset ni nj
    ni = 0
    nj = 0
    
    while nj < nj_max:
        while ni < ni_max:
            n_data[nj][ni] = round(o_lon_data[nj][ni], 2)*100 
            ni += 1
        
        if (nj % 10) == 0:
            print("in nj loop %d\n" % (nj))
        ni = 0
        nj += 1

    print("End of lon transformation \n")
    
    new_dataset.variables['lon'][:]  = n_data
    new_dataset.sync()
    

    new_dataset.close()
    
    old_dataset.close()




if __name__ == '__main__':
    transform_osi_saf_int_netcdf()
    #transform_osi_saf_netcdf()