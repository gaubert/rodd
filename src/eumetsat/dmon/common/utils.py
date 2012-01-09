# -*- coding: utf-8 -*-
'''
Created on Nov 15, 2011

@author: guillaume.aubert@eumetsat.int
'''
import sys
import StringIO
import traceback

ticks = u'▁▂▃▅▆▇'


def spark_string(ints):
    """Returns a spark string from given iterable of ints."""
    step = ((max(ints)) / float(len(ticks) - 1)) or 1
    return u' '.join(ticks[int(round(i / step))] for i in ints)


def spark_print(ints, stream=None):
    """Prints spark to given stream."""
    if stream is None:
        stream = sys.stdout
    stream.write(spark_string(ints).encode("utf-8"))
    
def human_time(secs):
    """
      format time in secs to human readable values
    """
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    
    if hours > 0:
        return '%02dh%02dm%02d' % (hours, mins, secs)
    elif mins > 0:
        return '%02dm%02ds' % (mins, secs)
    else:
        return '%02ds' % (secs)
    
    return '%02d:%02d:%02d' % (hours, mins, secs)
    
def human_size(size_bytes):
    """
    format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
    Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
    e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
    """
    if size_bytes == 1:
        # because I really hate unnecessary plurals
        return "1 byte"

    suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]

    num = float(size_bytes)
    for suffix, precision in suffixes_table:
        if num < 1024.0:
            break
        num /= 1024.0

    if precision == 0:
        formatted_size = "%d" % num
    else:
        formatted_size = str(round(num, ndigits=precision))

    return "%s %s" % (formatted_size, suffix)


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


if __name__ == '__main__': 
    #import collections
    
    #d = collections.deque([0,25,0,0,35,2,3,125,5,6], maxlen = 10)
    
    #spark_print(d)
    print(human_time(7465))