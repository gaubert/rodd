'''
Created on Nov 2, 2011

@author: guillaume.aubert@eumetsat.int
'''
import datetime

ZERO = datetime.timedelta(0) 

# A UTC class.    
class UTC(datetime.tzinfo):    
    """UTC Timezone"""    
    
    def utcoffset(self, a_dt):  
        ''' return utcoffset '''  
        return ZERO    
    
    def tzname(self, a_dt):
        ''' return tzname '''    
        return "UTC"    
        
    def dst(self, a_dt):  
        ''' return dst '''      
        return ZERO  

# pylint: enable-msg=W0613    
UTC_TZ = UTC()


def gemsdate_to_datetime(a_gemsdate):
    """
       Convert a gems date to a python datetime
       The GEMS Date format: yy.dayofyear.hh.mm.ss
    """
    return datetime.datetime.strptime(a_gemsdate, "%y.%j.%H.%M.%S")

def datetime_to_gemsdate(a_datetime):
    """
       Convert datetime to GEMS Date string
    """
    return a_datetime.strftime("%y.%j.%H.%M.%S")

def simpledate_to_gemsdate(a_simpledate):
    """
       Transform a simple date into a GEMS date
       simple date format: yyyy-mm-dd HH:MM:SS
    """
    the_date = datetime.datetime.strptime(a_simpledate, '%Y-%m-%d %H:%M:%S')
    return the_date.strftime("%y.%j.%H.%M.%S")

def gemsdate_to_simpledate(a_gemsdate):
    """
       transform a gemsdate into a simple date
    """
    d = gemsdate_to_datetime(a_gemsdate)
    return d.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    
    print(gemsdate_to_datetime("11.308.15.02.03"))
    
    print(datetime_to_gemsdate(gemsdate_to_datetime("11.308.15.02.03")))

    print(simpledate_to_gemsdate("2011-11-04 15:02:03"))
    
    print(gemsdate_to_simpledate(simpledate_to_gemsdate("2011-11-04 15:02:03")))

