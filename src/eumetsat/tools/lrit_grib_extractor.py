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

def read_MDD_dir(dir):
    """ read MDD dir """
    
    grib_output_dir = "/tmp/mdd5"
    bufr_output_dir = "/tmp/mdd5"
    #output_dir = "%s/gribs" % (dir)
    prefix     = "mdd5_data_%s"
    cpt = 0
    
    for file in dirwalk(dir):
        
        extract_grib_from_lrit_file(file, prefix % (cpt), grib_output_dir)
        extract_bufr_from_lrit_file(file, prefix % (cpt), bufr_output_dir)
        cpt += 1
    

def extract_grib_from_lrit_file(file_path, prefix, output_dir):
    """ read lrit file """
    
    fp = open(file_path, "rb")
    
    bs = BitString(fp)
    
    cpt=0
    
    print("==== Looking for Gribs in %s\n" %(file_path))
    
    # look for GRIB in hex 0x47524942
    f_val = bs.find('0x47524942', bytealigned=True)
     
    while f_val:
        
        begin= bs.pos
        
        print("** Found Grib in pos %s" % (bs.bytepos) )
        
        # read size
        grib_value = bs.read(32).hex
        size = bs.read('uint:24')*8
        
        #print("size in decimal = %s" %(size))
        
        #read all bits (end-begin)+1
        bs.pos = begin
        read_bits = bs.read(size)
        
        dest_fp = open("%s/%s_grib_%s.grb" % (output_dir, prefix, cpt), "wb")
        dest_fp.write(read_bits.tobytes())
        dest_fp.close()
        
        cpt +=1 
        
        #look for the next grib
        f_val = bs.find('0x47524942', start=bs.pos, bytealigned=True)

def extract_bufr_from_lrit_file(file_path, prefix, output_dir):
    """ read lrit file """
    
    file_size = os.path.getsize(file_path)
    
    fp = open(file_path, "rb")
    
    bs = BitString(fp)
    
    cpt=0
    
    print("==== Looking for Bufrs in %s\n" %(file_path))
    
    # look for BUFR in hex 0x42554652
    f_val = bs.find('0x42554652', bytealigned=True)
     
    while f_val:
        
        begin= bs.pos
        
        print("** Found Bufr in pos %s\n" % (begin) )
        
        # read size
        bufr_value = bs.read(32).hex
        size = bs.read('uint:24')
        
        print("size in decimal = %s" %(size))
        
        if size > file_size:
            print("Size read in bufr %d is bigger than the file size %d\n" %(size, file_size))
            return
        
        #read all bits (end-begin)+1
        bs.pos = begin
        read_bits = bs.read(size)
        
        dest_fp = open("%s/%s_bufr_%s.bufr" % (output_dir, prefix, cpt), "wb")
        dest_fp.write(read_bits.tobytes())
        dest_fp.close()
        
        cpt +=1 
        
        #look for the next grib
        f_val = bs.find('0x42554652', start=bs.pos, bytealigned=True)


if __name__ == '__main__':
    
    read_MDD_dir("/homespace/gaubert/MDDs/MDDJuly2011/MDD4")
    #read_lrit_file("/homespace/gaubert/MDDs/MDD-April2011/L-000-MSG2__-GTS_________-MDD_5____-000018___-201104040032-__","mdd5_201104040032_seg000018_","/homespace/gaubert/MDDs/MDD-April2011/grib-snd")
    
    