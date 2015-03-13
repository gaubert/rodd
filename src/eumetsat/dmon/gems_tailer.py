'''
Created on Nov 8, 2011

@author: guillaume.aubert@eumetsat.int
'''
import datetime
import time
import sys

#syntax coloring for terminal
import colorama

import eumetsat.dmon.common.time_utils as tu
import eumetsat.dmon.common.log_utils  as log_utils
import eumetsat.dmon.common.diss_parsing_utils as diss_parsing_utils
import eumetsat.dmon.common.utils as utils

import gems_feeder
from eumetsat.dmon.parsers import tellicastlog_parser, xferlog_parser

X_PARSER = xferlog_parser.XferlogParser()
S_PARSER = tellicastlog_parser.TellicastLogParser('tc-send')

'''
   add gems.logging parsers
   2011-11-10 09:16:21 W GEMS.logging: Entry detected: [11/11/10 09:15:29.813] WARN: de.eumetsat.GEMS.doftp.FtpHandler@4213a1b2 - could not transfer file [DVB_EU...
   2011-11-10 09:16:21 W GEMS.logging: Entry detected: [11/11/10 09:15:29.813] WARN: de.eumetsat.GEMS.doftp.FtpHandler@4213a1b2 - TransferHandler:putFile(): java...
   2011-11-10 09:16:21 W GEMS.logging: Entry detected: [11/11/10 09:15:29.814] WARN: FtpException: Putfilelist.doProcess FtpException: java.io.IOException: Agent...
'''


def print_in_green(a_str):
    """ print a string in green """
    return colorama.Fore.GREEN + a_str + colorama.Fore.RESET

def print_in_red(a_str):
    """ print in red """
    return colorama.Fore.RED + a_str + colorama.Fore.RESET

def get_string_to_print(lvl, a_str):
    '''
       black for info
       red   for warn of error
    '''
    if lvl in ['W','E']:
        return colorama.Fore.RED + a_str + colorama.Fore.RESET
    else:
        return a_str
        
class GEMSColPrinter(object):
    """
       Printer events in columns
    """
    
    log = log_utils.LoggerFactory.get_logger('GEMSColPrinter')
    
    @classmethod
    def print_line(cls, a_line_dict):
        """
           print a gems line in dissemination mode (without gems info but only the diss info)
        """
        
        app_type = diss_parsing_utils.guess_app(a_line_dict['msg'])

        if app_type == 'xferlog':
            result = X_PARSER.parse_one_line(a_line_dict['msg'])  
            
            (filename, service_dir) = diss_parsing_utils.get_xferlog_file_info(result['file'])
            
            #cut filenames longer than 80 chars
            if len(filename) > 80:
                filename = filename[:77] + '...'
             
            message = '%s %s %s %s (%s) uplinked in %s in %s sec' %(tu.datetime_to_compactdate(result['time']), \
                                                                               'ftpserv'.ljust(7),
                                                                               a_line_dict['lvl'], \
                                                                               filename.ljust(80), \
                                                                               diss_parsing_utils.get_human_readable_bytes(result['file_size']).ljust(9), \
                                                                               service_dir.ljust(25), \
                                                                               result['transfer_time'].ljust(2) )
             
            GEMSColPrinter.log.info(get_string_to_print(a_line_dict['lvl'], message))
            
        elif app_type == 'gems':
            GEMSColPrinter._simple_print_line(a_line_dict)
        elif app_type == 'tc-send':
            result = S_PARSER.parse_one_line(a_line_dict['msg'])  
            
            message ='%s %s %s %s' % (tu.datetime_to_compactdate(result['time']) , \
                                   'tcsend'.ljust(7), \
                                   a_line_dict['lvl']  , \
                                   result['msg'][:130].ljust(130))
            
            GEMSColPrinter.log.info(get_string_to_print(a_line_dict['lvl'], message))
            
    
    @classmethod
    def _simple_print_line(cls, a_line_dict):
        """
           print a gems line as it is
        """
        
            
        #for the moment remove micro seconds
        pos  = a_line_dict['time'].rfind('.')
            
        the_time = tu.gemsdate_to_simpledate(a_line_dict['time'][:pos]).center(19)
        lvl  = a_line_dict['lvl']
        
        #cut filenames longer than 80 chars
        if len(a_line_dict['msg']) > 139:
            message = a_line_dict['msg'][:136] + '...'
        else:
            message = a_line_dict['msg'][:139]
            
        msg  = message.ljust(139)
            
        #print('%s %s %s\n' %(time, lvl, msg))
        GEMSColPrinter.log.info(get_string_to_print(a_line_dict['lvl'],'%s %s %s %s' %(the_time, ' '.ljust(7), lvl, msg)))
        
class DissInfoPrinter(object):
    """
       Printer events in columns
    """
    
    @classmethod
    def print_line(cls, a_line_dict):
        """
           print a gems line
        """
        
        #for the moment remove micro seconds
        pos  = a_line_dict['time'].rfind('.')
        
        time = tu.gemsdate_to_simpledate(a_line_dict['time'][:pos]).center(19)
        lvl  = a_line_dict['lvl'].center(3)
        msg  = a_line_dict['msg'].center(80)
        
        print('%s %s %s\n' %(time, lvl, msg))
        

class GEMSTailer(object):
    '''
       Do like a Tail over GEMS events
    '''
    def __init__(self):
        pass
    
    def tail(self):
        '''
         tail
        '''
        
        end_time     = datetime.datetime.utcnow()
        
        start_time   = end_time - datetime.timedelta(0, 200)
        
        feeder = gems_feeder.GEMSExtractor(start_time = tu.datetime_to_gemsdate(start_time), \
                                           end_time   = tu.datetime_to_gemsdate(end_time), \
                                           severity   = ["A","W","I"], \
                                           facility   = ['DVB_EUR_UPLINK'])
        
        while True:
            last_line = None
            for line in feeder:
                last_line = line
                GEMSColPrinter.print_line(last_line)
            
            if not last_line:
                #print("sleep")
                time.sleep(10)
                #increase time window
                end_time   = datetime.datetime.utcnow()
            else:
                pos = last_line['time'].rfind('.')
                the_time = last_line['time'][:pos]
                start_time = tu.gemsdate_to_datetime(the_time)
                
                start_time = start_time + datetime.timedelta(0, 1)
                end_time   = datetime.datetime.utcnow()
            
            feeder = gems_feeder.GEMSExtractor(start_time = tu.datetime_to_gemsdate(start_time), \
                                               end_time   = tu.datetime_to_gemsdate(end_time), \
                                               severity   = ["A","W","I"], \
                                               facility   = ['DVB_EUR_UPLINK'])
            
def bootstrap_run():
    """ temporary bootstrap """
    
    try:
        #log in stdout
        log_utils.LoggerFactory.setup_simple_stdout_handler() 
        
        tailer = GEMSTailer()
        
        tailer.tail()
        
        sys.exit(1)
    
    except KeyboardInterrupt:
        #CTRL^C pressed so silently quit
        sys.exit(0)
    except Exception, e:
        # report error and proceed
        error_str = utils.get_exception_traceback()
        
        log = log_utils.LoggerFactory.get_logger('bootstrap_run')
        
        log.error("Received error %s. traceback = %s\nPlease contact your administrator." %(e, error_str))
        
        sys.exit(1)
    
if __name__ == '__main__':
    bootstrap_run()