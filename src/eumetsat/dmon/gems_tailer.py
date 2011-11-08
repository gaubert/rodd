'''
Created on Nov 8, 2011

@author: guillaume.aubert@eumetsat.int
'''
import datetime
import time_utils as tu
import time
import gems_feeder

class GEMSTailer(object):
    '''
       
    '''


    def __init__(selfparams):
        '''
          Listen to new events on GEMS
        '''
    
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
                print last_line
            
            if not last_line:
                print("sleep")
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