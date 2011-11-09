'''
Created on Nov 8, 2011

@author: guillaume.aubert@eumetsat.int
'''
import datetime
import time

import time_utils as tu
import log_utils
import gems_feeder
import diss_parsing_utils
import xferlog_parser
import tellicastlog_parser

import colorama

X_PARSER = xferlog_parser.XferlogParser()
S_PARSER = tellicastlog_parser.TellicastLogParser('tc-send')


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
             
            message = '%s %s %s (%s) uplinked in %s in %s sec' %(result['time'], \
                                                                               a_line_dict['lvl'], \
                                                                               filename.ljust(80), \
                                                                               diss_parsing_utils.get_human_readable_bytes(result['file_size']).ljust(9), \
                                                                               service_dir.ljust(25), \
                                                                               result['transfer_time'].ljust(2) )
             
            GEMSColPrinter.log.info(get_string_to_print(a_line_dict['lvl'], message))
            
        elif app_type == 'gems':
            GEMSColPrinter._simple_print_line(get_string_to_print('W', a_line_dict['msg']))
        elif app_type == 'tc-send':
            result = S_PARSER.parse_one_line(a_line_dict['msg'])  
            
            message ='%s %s %s' % (result['time'] , \
                                   result['lvl']  , \
                                   result['msg'])
            
            GEMSColPrinter._simple_print_line(get_string_to_print(result['lvl'], message))
            
    
    @classmethod
    def _simple_print_line(cls, a_line_dict):
        """
           print a gems line as it is
        """
        
            
        #for the moment remove micro seconds
        pos  = a_line_dict['time'].rfind('.')
            
        the_time = tu.gemsdate_to_simpledate(a_line_dict['time'][:pos]).center(19)
        lvl  = a_line_dict['lvl'].center(3)
        
        #cut filenames longer than 80 chars
        if len(a_line_dict['msg']) > 130:
            message = a_line_dict['msg'][:127] + '...'
        else:
            message = a_line_dict['msg'][:130]
            
        msg  = message.ljust(130)
            
        #print('%s %s %s\n' %(time, lvl, msg))
        GEMSColPrinter.log.info('%s %s %s' %(the_time, lvl, msg))
        
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
            
            
if __name__ == '__main__':
    
    log_utils.LoggerFactory.setup_simple_stderr_handler() 
   
    tailer = GEMSTailer()
    
    tailer.tail()