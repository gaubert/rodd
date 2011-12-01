'''
Created on Nov 2, 2011

@author: guillaume.aubert@eumetsat.int
'''
import datetime
import re

ZERO = datetime.timedelta(0) 

DATETIME_TYPE = type(datetime.datetime.now())

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

# cpnversion elements

GEMSDATE_PATTERN    = "%y.%j.%H.%M.%S"
SIMPLEDATE_PATTERN  = '%Y-%m-%d %H:%M:%S'
STDDATE_PATTERN     = '%Y-%m-%dT%H:%M:%S'
COMPACTDATE_PATTERN = '%Y%m%d %H:%M:%S'

GEMSDATE   = "GEMSDATE"
SIMPLEDATE = "SIMPLEDATE"
STDDATE    = "STDDATE"

#11.321.08.30.45.454
#simplistic regular expression to recognise the date format
GEMSDATE_RE   = re.compile("\d\d\.\d\d\d\.\d\d\.\d\d\.\d\d(?P<millisec>(\.\d{0,3})?)")
SIMPLEDATE_RE = re.compile("\d\d\d\d-\d\d\-\d\d\ \d\d:\d\d:\d\d(\.\d{0,3})?")
STDDATE_RE    = re.compile("\d\d\d\d-\d\d\-\d\d\T\d\d:\d\d:\d\d(\.\d{0,3})?")

SUPPORTED_DATE_FORMATS_LIST = [ 'gems: yy.dayofyear.HH.MM.SS', 'simple: yyyy-mm-dd HH:MM:SS', 'standard: yyyy-mm-ddTHH:MM:SS' ]

#factory map for the conversion
GUESS_DATE_MAP = { 
                   GEMSDATE    : GEMSDATE_RE ,\
                   SIMPLEDATE  : SIMPLEDATE_RE,\
                   STDDATE     : STDDATE_RE
                 }

PATTERN_DATE_MAP = {
                    GEMSDATE    : GEMSDATE_PATTERN , \
                    SIMPLEDATE  : SIMPLEDATE_PATTERN, \
                    STDDATE     : STDDATE_PATTERN
                   }

def gemsdate_to_datetime(a_gemsdate):
    """
       Convert a gems date to a python datetime
       The GEMS Date format: yy.dayofyear.hh.mm.ss
    """
    return datetime.datetime.strptime(a_gemsdate, GEMSDATE_PATTERN)

def datetime_to_gemsdate(a_datetime):
    """
       Convert datetime to GEMS Date string
    """
    return a_datetime.strftime(GEMSDATE_PATTERN)

def datetime_to_simpledate(a_datetime):
    """
       Convert datetime to simple date
    """
    return a_datetime.strftime(SIMPLEDATE_PATTERN)

def datetime_to_compactdate(a_datetime):
    """
       Convert datetime to simple date
    """
    return a_datetime.strftime(COMPACTDATE_PATTERN)

def datetime_to_time(a_datetime):
    """
       Convert datetime to simple date
    """
    if a_datetime:
        return a_datetime.strftime('%H:%M:%S')
    
    return None

def simpledate_to_gemsdate(a_simpledate):
    """
       Transform a simple date into a GEMS date
       simple date format: yyyy-mm-dd HH:MM:SS
    """
    the_date = datetime.datetime.strptime(a_simpledate, SIMPLEDATE_PATTERN)
    return the_date.strftime(GEMSDATE_PATTERN)



def gemsdate_to_simpledate(a_gemsdate):
    """
       transform a gemsdate into a simple date
    """
    d = gemsdate_to_datetime(a_gemsdate)
    return d.strftime(SIMPLEDATE_PATTERN)

def guess_date_format(a_date):
    """
       Find the used string date format
       GEMSDATE or SIMPLEDATE
    """
    for type, regexpr in GUESS_DATE_MAP.items():
        matched = regexpr.match(a_date)
        if matched:
            gi = matched.groupdict()
            print(gi)
            return type
    
    # no type found so raise an exception
    raise Exception("%s is not in a know date format %s" % (a_date, SUPPORTED_DATE_FORMATS_LIST))

    
def convert_date_str_to_datetime(a_date_str):
    """
       If the date format is part of one of the supported format. Convert it to datetime
    """
    date_pattern = PATTERN_DATE_MAP.get(guess_date_format(a_date_str), None)
    
    if date_pattern:        
        return datetime.datetime.strptime(a_date_str, date_pattern)
    else:
        raise Exception("No date pattern found for %s\n" %(a_date_str))
    
def e2datetime(a_epoch):
    """
        convert epoch time in datetime

            Args:
               a_epoch: the epoch time to convert

            Returns: a datetime
    """

    #utcfromtimestamp is not working properly with a decimals.
    # use floor to create the datetime
#    decim = decimal.Decimal('%s' % (a_epoch)).quantize(decimal.Decimal('.001'), rounding=decimal.ROUND_DOWN)

    new_date = datetime.datetime.utcfromtimestamp(a_epoch)

    return new_date

def datetime2e(a_date):
    """
        convert datetime in epoch
        Beware the datetime as to be in UTC otherwise you might have some surprises
            Args:
               a_date: the datertime to convert

            Returns: a epoch time
    """
    return calendar.timegm(a_date.timetuple())

if __name__ == '__main__':
    
    print(gemsdate_to_datetime("11.308.15.02.03"))
    
    print(datetime_to_gemsdate(gemsdate_to_datetime("11.308.15.02.03")))

    print(simpledate_to_gemsdate("2011-11-04 15:02:03"))
    
    print(gemsdate_to_simpledate(simpledate_to_gemsdate("2011-11-04 15:02:03")))
    
    print(guess_date_format("2011-11-04 15:02:03"))
    
    print(guess_date_format("11.308.15.02.03"))
    
    print(guess_date_format("117.308.15.02.03"))

