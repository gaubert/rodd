import os
import time
import itertools
import gc
import base64
import StringIO
import sys
import traceback

class curry:
    """ Class used to implement the currification (functional programming technic) :
        Create a function from another one by instanciating some of its parameters.
        For example double = (operator.mul,2), res = double(4) = 8
    """
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.pending = args[:]
        self.kwargs = kwargs.copy()
        
    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        return self.fun(*(self.pending + args), **kw) #IGNORE:W0142



def forname(modname, classname):
    """ high level api: reflection, get a class object and load its corresponding module from a string module and class name 
        If modulename is "" the local module ctbto.common is taken
    """
    module = __import__(modname,globals(),locals(),['NoName'],-1)
    classobj = getattr(module, classname)
    return classobj 

def new_instance(modname,classname,*args):
    """ instance a class from a string class and module name """
    
    if modname == None:
        modname = ""
    
    classobj = forname(modname,classname)
    return classobj(*args) #IGNORE:W0142

def round_as_string(aFloat,aNbDigits):
    """ Round a float number up to aNbDigits after the .
        printf is used to do that.
    
        Args:
           aFloat:    the float to round
           aNbDigits: the nb of digits to round after 
           
        Returns:
           a string representation of the rounded number
    
        Raises:
           exception
    """
    assert aNbDigits > 0
    
    # create string in two steps. There is surely a better way to do it in one step
    formatting_str = '%.' + '%sf'%(aNbDigits)
    
    return formatting_str%(float(aFloat))

def round(aFloat,aNbDigits):
    """ Round a float number up to aNbDigits after the .
        printf is used to do that.
    
        Args:
           aFloat:    the float to round
           aNbDigits: the nb of digits to round after 
           
        Returns:
           a rounded nb a a float
    
        Raises:
           exception
    """
    return float(round_as_string(aFloat, aNbDigits))

def checksum(aString):
    """checksum the passed string. This is a 32 bits checksum
    
        Args:
           params: aString. String from which the checksum is computed 
           
        Returns:
           return the checksum of the passed string
    
        Raises:
           exception
    """
        
    chksum = 0L
    toggle = 0

    i = 0
    while i < len(aString):
        ch = aString[i]
        if ord(ch) > 0:
            if toggle: chksum = chksum << 1
            chksum = chksum + ord(ch)
            chksum = chksum & 0X7fffffff
            toggle = not toggle
        else:
            chksum = chksum + 1
        i = i + 1

    return chksum

#####################################
#
#  check if a file exist and otherwise raise an exception
#
################################### 
def file_exits(aFilePath):
    
    # asserting input parameters
    if aFilePath == None:
        raise Exception(-1,"passed argument aFilePath is null")
    else:
        # check if file exits
        if not os.path.exists(aFilePath):
            raise Exception(-1,"the file %s does not exits"%(aFilePath))
        
def makedirs(aPath):
    """ my own version of makedir """
    
    if os.path.isdir(aPath):
        # it already exists so return
        return
    elif os.path.isfile(aPath):
        raise OSError("a file with the same name as the desired dir, '%s', already exists."%(aPath))

    os.makedirs(aPath)
    
def __rmgeneric(path, __func__):
    """ private function that is part of delete_all_under """
    try:
        __func__(path)
        #print 'Removed ', path
    except OSError, (errno, strerror): #IGNORE:W0612
        print """Error removing %(path)s, %(error)s """%{'path' : path, 'error': strerror }
            
def delete_all_under(path,delete_top_dir=False):
    """ delete all files and directories under path """

    if not os.path.isdir(path):
        return
    
    files=os.listdir(path)

    for x in files:
        fullpath=os.path.join(path, x)
        if os.path.isfile(fullpath):
            f=os.remove
            __rmgeneric(fullpath, f)
        elif os.path.isdir(fullpath):
            delete_all_under(fullpath)
            f=os.rmdir
            __rmgeneric(fullpath, f)
    
    if delete_top_dir:
        os.rmdir(path)


def ftimer(func, args, kwargs, result = [], number=1, timer=time.time): #IGNORE:W0102
    """ time a func or object method """
    it = itertools.repeat(None, number)
    gc_saved = gc.isenabled()
    
    try:
        gc.disable()
        t0 = timer()
        for i in it:                  #IGNORE:W0612
            r = func(*args, **kwargs) #IGNORE:W0142
            if r is not None:
                result.append(r)
                t1 = timer()
    finally:
        if gc_saved:
            gc.enable()
        
    return t1 - t0

def dirwalk(dir):
    """
     Walk a directory tree, using a generator.
     This implementation returns only the files in all the subdirectories.
     Beware, this is a generator.
    """
    for f in sorted(os.listdir(dir)):
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath):  # recurse into subdir
                yield x
        else:
            yield fullpath


def obfuscate_string(a_str):
    """ use base64 to obfuscate a string """
    return base64.b64encode(a_str)

def deobfuscate_string(a_str):
    """ deobfuscate a string """
    return base64.b64decode(a_str)


def get_exception_traceback():
    """
            return the exception traceback (stack info and so on) in a string
        
            Args:
               None
               
            Returns:
               return a string that contains the exception traceback
        
            Raises:
               
    """
    the_file = StringIO.StringIO()
    exception_type, exception_value, exception_traceback = sys.exc_info() #IGNORE:W0702
    traceback.print_exception(exception_type, exception_value, exception_traceback, file = the_file)
    return the_file.getvalue()
 


#####################################
#
#  print crudely a dict
#
################################### 
def printDict(di, format="%-25s %s"):
    """ pretty print a dictionary """
    for (key, val) in di.items():
        print format % (str(key)+':', val)
        

def printInFile(aStr,aPath):
    #check if it is a path or a file
     
    if type(aPath) in (type('str'),type(u'str')):
        f = open(aPath,"w")
    else:
        f = aPath
    
    f.write(aStr)
    f.close()



            
if __name__ == "__main__":

    print "Hello"