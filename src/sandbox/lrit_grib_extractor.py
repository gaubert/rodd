'''
Created on Oct 18, 2010

@author: guillaume.aubert@gmail.com
'''
import os
from bitstring import BitString


def dirwalk(dir):
    """
     Walk a directory tree, using a generator.
     This implementation returns only the files in all the subdirectories.
     Beware, this is a generator.
    """
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath):  # recurse into subdir
                yield x
        else:
            yield fullpath

def read_MDD_dir():
    """ read MDD dir """
    
    output_dir = "/homespace/gaubert/faulty-grib"
    prefix="pref_%s"
    cpt = 0
    
    for file in dirwalk("/homespace/gaubert/faulty-grib"):
        
        read_lrit_file(file, prefix % (cpt), output_dir)
        cpt += 1
    

def read_lrit_file(file_path, prefix, output_dir):
    """ read lrit file """
    
    fp = open(file_path, "rb")
    
    bs = BitString(fp)
    
    cpt=0
    
    # look for GRIB in hex 0x47524942
    f_val = bs.find('0x47524942', bytealigned=True)
     
    while f_val:
        
        begin= bs.pos
        
        # read size
        grib_value = bs.read(32).hex
        size = bs.read('uint:24')*8
        
        print("size in decimal = %s" %(size))
        
        #read all bits (end-begin)+1
        bs.pos = begin
        read_bits = bs.read(size)
        
        dest_fp = open("%s/%s_grib_%s.grb" % (output_dir, prefix, cpt), "wb")
        dest_fp.write(read_bits.tobytes())
        dest_fp.close()
        
        cpt +=1 
        
        #look for the next grib
        f_val = bs.find('0x47524942', start=bs.pos, bytealigned=True)
         
        
    
    # look for GRIB in hex 47524942
    found_gen = bs.findall('0x47524942', bytealigned=True)
    #print(found, bs.bytepos)
    for found in found_gen:
        print(found, bs.bytepos)



if __name__ == '__main__':
    
    read_MDD_dir()
    
    