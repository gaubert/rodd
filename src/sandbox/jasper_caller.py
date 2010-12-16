'''
Created on Nov 17, 2010

@author: gaubert
'''
from ctypes import *

PATH_TO_JASPER="/homespace/gaubert/ecmwf-libs/inst/jasper/lib/libjasper.so"

def main():
    jasper = cdll.LoadLibrary(PATH_TO_JASPER)
   
    print(dir(jasper))
    
    img = jasper.jas_image_t()

if __name__ == '__main__':
    main()