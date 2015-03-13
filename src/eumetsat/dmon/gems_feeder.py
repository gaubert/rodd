'''
Created on Nov 4, 2011

@author: guillaume.aubert@eumetsat.int
'''
import re
import urllib

import requests
from BeautifulSoup import BeautifulSoup

import eumetsat.dmon.common.time_utils as time_utils
import eumetsat.dmon.common.log_utils  as log_utils

class GEMSHTMLParser(object):
    '''
       Parse a GMES page and return the GEMS log events
    '''
    
    log = log_utils.LoggerFactory.get_logger('GEMSHTMLParser')
    
    
    @classmethod
    def get_GEMS_events(cls, content):
        '''
           return the gems events
        '''
        
        results = []
        
        data_table = BeautifulSoup(content).find('table', width='100%')
        
        if data_table:
            #check that we do have data and not an empty table otherwise return []
            rows = data_table.findAll('tr')
            
            if rows and len(rows) >= 2:
                for row in rows[2:]:
                    
                    cols = row.findAll('td')
                    
                    if len(cols) == 6:
                        time     = cols[0].string
                        facility = cols[1].string
                        host     = cols[2].string
                        agent    = cols[3].string
                        lvl      = cols[4].string
                        msg      = cols[5].string
                        
                        results.append({ 'time'    : time, 'facility' : facility, \
                                  'host' : host, 'agent'  :  agent, \
                                  'lvl'  : lvl , 'msg'    :  msg
                               })
        
        return results
    
    @classmethod
    def get_next_url(cls, content):
        '''
           Return the next url if there are any or none
        '''
        
        next_elem = BeautifulSoup(content).find('a', href = re.compile('HistoryFilterDisplay\.jsp\?.*'))
        if next_elem:
            for (name, val) in next_elem.attrs:
                return (val if name == 'href' else None)
        
        return
    
    @classmethod
    def get_GEMS_facilities(cls, content):
        """
           Return the list of gems facilities
        """
        results = []
        
        data_table = BeautifulSoup(content).find('table', width='100%')
        
        if data_table:
            rows = data_table.findAll('tr')
            
            if rows:
                #skip first 2 rows that define column headers and co
                for row in rows[2:]:
                    cols = row.findAll('td')
                    if len(cols) == 8:
                        facility = cols[1].string
                        results.append(facility)
                 
        return results   
                

class GEMSExtractor(object):
    '''
       Extract Event from GEMS
    '''
    log = log_utils.LoggerFactory.get_logger('GEMSExtractor')
    
    #used to get a JSESSIONID
    START_URL  = 'http://omasif/GEMS/HistoryFilterRetry.jsp?startTime=11.308.15.02.03&endTime=11.308.15.12.03&severity=A&severity=W&severity=I&facility=DVB_EUR_UPLINK'
    
    FAC_URL    = 'http://omasif/GEMS/index2.jsp'
    
    URL_PREFIX   = 'http://omasif/GEMS/'
    D_URL_PREFIX = 'HistoryFilterController.jsp?'
    
    #Max number of elements retrieved
    MAX_NB_ELEMENTS = 400
                
    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        self._cookies = None
        self._url     = None
        self._gen     = None
        
        self._url = self.parse_GEMS_request(**kwargs)
        GEMSExtractor.log.debug("request_url\n%s\n" % (self._url))
    
    @classmethod
    def _get_session_id(cls):
        """
          get the session id that is necessary to get to browse GEMS
        """
        req = requests.get(GEMSExtractor.START_URL)
        return req.cookies
        
    @classmethod
    def get_all_GEMS_facilities(cls):
        """
           Get all the GEMS facilities available
        """
        GEMSExtractor.log.debug("request GEMS session id\n")
        
        #get session id
        cookies = GEMSExtractor._get_session_id()
        
        GEMSExtractor.log.debug("request GEMS facilities\n")
        
        url = GEMSExtractor.FAC_URL
        
        GEMSExtractor.log.debug("###### HTTP REQUEST ######\n")
        
        req = requests.get(url, cookies = cookies)
        
        return GEMSHTMLParser.get_GEMS_facilities(req.content)
       
        
    def parse_GEMS_request(self, **kwargs):
        """
           Parse the parameters in GEMS
        """
        #look for start_time
        s_time = kwargs.get('start_time', '')
        #convert to GEMS time if it is a simple date
        
        if type(s_time) == time_utils.DATETIME_TYPE:
            s_time = time_utils.datetime_to_gemsdate(s_time)
        else:
            #convert string datetime to gems datetime
            s_time = time_utils.simpledate_to_gemsdate(convert_date_str_to_datetime(s_time))
           
        e_time = kwargs.get('end_time', '')
        
        if type(e_time) == time_utils.DATETIME_TYPE:
            e_time = time_utils.datetime_to_gemsdate(e_time)
        else:
            #convert string datetime to gems datetime
            e_time = time_utils.simpledate_to_gemsdate(convert_date_str_to_datetime(e_time))
        
        start_time = 'startTime=%s' % (s_time)
        end_time   = '&endTime=%s' % (e_time)
        
        severities = ''
        str_severities = kwargs.get('severity', None)
        if str_severities:
            for severity in str_severities:
                if severity in ['I', 'A', 'W']:
                    severities = ''.join([severities, '&severity=%s' % (severity)])
        else:
            #default equals all severities
            #maybe it should be moved in other object
            severities = '&severity=I&severity=A&severity=W'

        facilities = ''
        for facility in kwargs.get('facility', []):
            facilities += '&facility=%s' % (facility)
            
        hosts = ''
        for host in kwargs.get('host', []):
            hosts += '&host=%s' % (host)

        processes = ''
        for process in kwargs.get('process', []):
            processes += '&process=%s' % (process)
            
        
        #url encode the elements
        # for the moment always regExp
        search = '&search=%s&regExp=1' % (urllib.quote(kwargs.get('search','')))
        
        request = "%s%s%s%s%s%s%s%s%s&pageSize=%s&x=50&y=6" % ( GEMSExtractor.URL_PREFIX, \
                                                                GEMSExtractor.D_URL_PREFIX, \
                                                                start_time, end_time, \
                                                                severities, facilities, \
                                                                hosts, processes, \
                                                                search, GEMSExtractor.MAX_NB_ELEMENTS)
        
        GEMSExtractor.log.debug("request =%s\n" %(request))
      
        return request   
        
    def set_url_to_parse(self, a_url):
        '''
          Define the URL to call
        '''
        self._url = a_url
    
    def _get_gems_data_gen(self):
        """
          Create the parsers generator
        """
        GEMSExtractor.log.debug("get session id form gems\n")
        
        self._cookies = self._get_session_id()
        
        GEMSExtractor.log.debug("request GEMS logs\n")
        
        url = self._url
        
        while url:
        
            GEMSExtractor.log.debug("###### HTTP REQUEST ######\n")
            req = requests.get(url, cookies = self._cookies)
            
            GEMSExtractor.log.debug("###### PARSING ######\n")
            next_url   = GEMSHTMLParser.get_next_url(req.content)
            
            gems_lines = GEMSHTMLParser.get_GEMS_events(req.content)
            
            for line in gems_lines:
                yield line
            
            url = '%s%s' % (GEMSExtractor.URL_PREFIX, next_url) if next_url else None
        
        return
        
        
    
    def __iter__(self):
        """ 
            
        """
        if not self._gen:
            self._gen = self._get_gems_data_gen()
        
        return self

    def next(self):
        """
           Return the next token
            
           Returns:
               return next found token 
        """
        
        # if no generator have been created first do it and call next
        if self._gen == None:
            self._gen = self._get_gems_data_gen()
        
        return self._gen.next() #pylint: disable-msg=E1103
    
    
    