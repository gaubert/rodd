'''
Created on Mar 28, 2011

@author: gaubert
'''
from netCDF4 import Dataset
import numpy
import sys

def paeth_predictor(a, b, c):
    """ calculate paeth predictor with
        c -- b
        |    |
        a -- x 
        
        With x is the point you are looking at.
    """
    
    p  = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    
    # return nearest of a,b,c,
    # breaking ties in order a,b,c.
    if (pa <= pb) and (pa <= pc):
        return a
    elif (pb <= pc):
        return b
    else:
        return c


def get_paeth_value(a, b, c, raw_val):
    """ get value 
    
        To encode
        Paeth(i,j) = Raw(i,j) - PaethPredictor(Raw(i-1,j), Raw(i,j-1), Raw(i-1,j-1)) 
        
        To decode the Paeth filter Raw(i,j) = Paeth(i,j) - PaethPredictor(Raw(i-1,j), Raw(i,j-1), Raw(i-1,j-1)) 
    """
    return (raw_val - paeth_predictor(a, b, c))

def get_raw_value(a, b, c, encoded_val):
    """ decode the value """
    return (encoded_val + (paeth_predictor(a, b, c)))

def netcdf_test():
    """ netcdf test """ 
    dataset = Dataset("/homespace/gaubert/20101206-EUR-L2P_GHRSST-SSTsubskin-AVHRR_METOP_A-eumetsat_sstmgr_metop02_20101206_000103-v01.7-fv01.0.nc",'a')
    
    new_dataset = Dataset('/homespace/gaubert/file_cp.nc','a')

    
    
    
    # get dimensions from the old dataset
    nj_max = len(dataset.dimensions['nj'])
    ni_max = len(dataset.dimensions['ni'])
    
    nj = 0
    ni = 0
    
    n_data = numpy.zeros((nj_max, ni_max), dtype=float)
    
    for elem in ('lat','lon'):
        data = dataset.variables[elem][:]
        while nj < nj_max:
            line = ""
            while ni < ni_max:
                
                #calculate a, b , c
                ni_1 = ni - 1 
                nj_1 = nj - 1
                
                a = 0 if (ni_1 < 0) else data[nj][ni_1]
                b = 0 if (nj_1 < 0) else data[nj_1][ni]
                c = 0 if ( (ni_1 < 0 or nj_1 < 0) ) else data[nj_1][ni_1]
                
                n_data[nj][ni] = get_paeth_value(a, b, c, data[nj][ni])
                
                line += ", %f" % (n_data[nj][ni])
                ni += 1
        
            #print(line)
            ni = 0
            nj += 1
        
        new_dataset.variables[elem][:]  = n_data
        new_dataset.sync()
    
    

if __name__ == '__main__':
    
    """val = -21.388
    a   = -21.3765
    b   = -21.3061
    c   = -21.2941
    
    predictor = paeth_predictor(a, b, c)
    paeth_val = get_paeth_value(a, b, c, val)
    dec_val   = get_raw_value(a, b, c, paeth_val)
    
    print("orig val = %f\n" %(val))
    print("predictor = %f\n" %(predictor))
    print("paeth_val = %f\n" % (paeth_val))
    print("decoded_val = %f\n" %(dec_val))
    """
    
    netcdf_test()