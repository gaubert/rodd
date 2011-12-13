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
    stream.write(spark_string(ints))

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