'''
Created on Nov 8, 2011

@author: guillaume.aubert@eumetsat.int
'''
import datetime
import time_utils as tu
import time
import gems_feeder
import string


class GEMSColPrinter(object):
    """
       Printer events in columns
    """
    
    @classmethod
    def print_line(cls, a_line_dict):
        """
           print a gems line
        """
        
        time = string.center(tu.gemsdate_to_simpledate(a_line_dict['time']), 10)
        lvl  = string.center(a_line_dict['lvl'], 5)
        msg  = string.ljust(a_line_dict['msg'], 80)
        
        print('%s  %s  %s\n' %(time, lvl, msg))
        
        

class GEMSTailer(object):
    '''
       Do like a Tail over GEMS events
    '''
    def __init__(self, params):
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
            print("request new line")
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

    tailer = GEMSTailer()
    
    tailer.tail()