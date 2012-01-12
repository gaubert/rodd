'''
Created on Nov 9, 2011

@author: guillaume.aubert@eumetsat.int
'''
import sys

import logbook


class StdoutHandler(logbook.StreamHandler):
    """A handler that writes to what is currently at stdout. At the first
glace this appears to just be a :class:`StreamHandler` with the stream
set to :data:`sys.stdout` but there is a difference: if the handler is
created globally and :data:`sys.stdout` changes later, this handler will
point to the current `stdout`, whereas a stream handler would still
point to the old one.
"""

    def __init__(self, level=logbook.base.NOTSET, format_string=None, filter=None,
                 bubble=False):
        logbook.StreamHandler.__init__(self, logbook.base._missing, level, format_string,
                               None, filter, bubble)

    @property
    def stream(self):
        return sys.stdout

class LoggerFactory(object):
    '''
       My Logger Factory
    '''
    
    @classmethod
    def get_logger(cls, name):
        """
          Simply return a logger
        """
        return logbook.Logger(name)
    
    
    @classmethod
    def setup_simple_stderr_handler(cls):
        """
           Push a stderr handler logging only the message (no timestamp)
        """
        
        null_handler = logbook.NullHandler()
        
        handler      = logbook.StderrHandler(format_string='{record.message}', level = 2, bubble = False)
         
        # first stack null handler to not have anything else logged 
        null_handler.push_application()
        # add Stderr Handler
        handler.push_application() 
    
    @classmethod
    def setup_simple_stdout_handler(cls):
        """
           Push a stderr handler logging only the message (no timestamp)
        """
        
        null_handler = logbook.NullHandler()
        
        handler      = StdoutHandler(format_string='{record.message}', level = 2, bubble = False)
         
        # first stack null handler to not have anything else logged 
        null_handler.push_application()
        # add Stderr Handler
        handler.push_application() 
    
    @classmethod
    def setup_simple_file_handler(cls, file_path, level = 2):
        """
           Push a file handler logging only the message (no timestamp)
        """
        
        null_handler = logbook.NullHandler()
        
        handler      = logbook.FileHandler(file_path, format_string='{record.message}', level = level, bubble = False)
         
        # first stack null handler to not have anything else logged 
        null_handler.push_application()
        # add Stderr Handler
        handler.push_application() 
        
