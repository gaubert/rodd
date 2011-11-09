'''
Created on Nov 9, 2011

@author: guillaume.aubert@eumetsat.int
'''

import logbook

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
        
