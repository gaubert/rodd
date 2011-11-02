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
