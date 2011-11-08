'''
Created on Nov 4, 2011

@author: guillaume.aubert@eumetsat.int
'''
import re
import requests
import time_utils

#import html5lib
from BeautifulSoup import BeautifulSoup

class GEMSHTMLParser(object):
    '''
       Parse a GMES page and return the GEMS log events
    '''
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
                        ip       = cols[0].string
                        facility = cols[1].string
                        host     = cols[2].string
                        agent    = cols[3].string
                        lvl      = cols[4].string
                        msg      = cols[5].string
                        
                        results.append({ 'ip'    : ip, 'facility' : facility,\
                                  'host' : host, 'agent'  :  agent, \
                                  'lvl'  : lvl , 'msg'    :  msg
                               })
        
        return results
    
    @classmethod
    def get_next_url(self, content):
        '''
           Return the next url if there are any or none
        '''
        
        next_elem = BeautifulSoup(content).find('a', href = re.compile('HistoryFilterDisplay\.jsp\?.*'))
        if next_elem:
            for (name, val) in next_elem.attrs:
                return (val if name == 'href' else None)
        
        return

class GEMSExtractor(object):
    '''
       Extract Event from GEMS
    '''

    #used to get a JSESSIONID
    START_URL  = 'http://omasif/GEMS/HistoryFilterRetry.jsp?startTime=11.308.15.02.03&endTime=11.308.15.12.03&severity=A&severity=W&severity=I&facility=DVB_EUR_UPLINK'
    
    URL_PREFIX   = 'http://omasif/GEMS/'
    D_URL_PREFIX = 'HistoryFilterController.jsp?'
    
    # to access the data
    #DATA_URL   = 'http://omasif/GEMS/HistoryFilterController.jsp?startTime=11.308.15.02.03&severity=A&endTime=11.308.15.02.19&severity=W&severity=I&facility=DVB_EUR_UPLINK&host=&process=&search=&pageSize=400&x=50&y=6'
    #start_time, end_time, level, 
    DATA_URL   = 'http://omasif/GEMS/HistoryFilterController.jsp?startTime=%s&severity=A&endTime=%s&severity=W&severity=I&facility=DVB_EUR_UPLINK&host=&process=&search=&pageSize=400&x=50&y=6'
    DATA_URL1  = 'http://omasif/GEMS/HistoryFilterController.jsp?start_time=11.308.15.02.03&end_time=11.308.15.12.03&facility=D&facility=V&facility=B&facility=_&facility=E&facility=U&facility=R&facility=_&facility=U&facility=P&facility=L&facility=I&facility=N&facility=K&search=&pageSize=400&x=50&y=6'
                
    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        self._cookies = None
        self._url     = None
        self._gen     = None
        
        self._url = self.parse_GEMS_request(**kwargs)
        print("request_url\n%s\n" % (self._url))
        
    def parse_GEMS_request(self, **kwargs):
        """
           Parse the parameters in GEMS
        """
        
        #look for start_time
        s_time = kwargs.get('start_time', '')
        #convert to GEMS time if it is a simple date
        if time_utils.guess_date_format(s_time) == time_utils.SIMPLEDATE:
           s_time = time_utils.simpledate_to_gemsdate(s_time)
           
        e_time = kwargs.get('end_time', '')
        #convert to GEMS time if it is a simple date
        if time_utils.guess_date_format(e_time) == time_utils.SIMPLEDATE:
           e_time = time_utils.simpledate_to_gemsdate(e_time)
        
        start_time = 'startTime=%s' % (s_time)
        end_time   = '&endTime=%s' % (e_time)
        
        severities = ''
        for severity in kwargs.get('severity', []):
            if severity in ['I','A','W']:
                severities = ''.join([severities, '&severity=%s' % (severity)])

        facilities = ''
        for facility in kwargs.get('facility', []):
            facilities += '&facility=%s' % (facility)
            
        hosts = ''
        for host in kwargs.get('host', []):
            hosts += '&host=%s' % (host)

        processes = ''
        for process in kwargs.get('process', []):
            processes += '&process=%s' % (process)
            
            
        search = '&search=%s' % (kwargs.get('search',''))
        
        request = "%s%s%s%s%s%s%s%s%s&pageSize=400&x=50&y=6" % ( GEMSExtractor.URL_PREFIX, GEMSExtractor.D_URL_PREFIX, start_time, end_time, severities, facilities, hosts, processes, search)
      
        return request   
    
    def _get_session_id(self):
        """
          get the session id that is necessary to get to browse GEMS
        """
        r = requests.get(GEMSExtractor.START_URL)
        self._cookies = r.cookies
        
    def set_url_to_parse(self, a_url):
        '''
          Define the URL to call
        '''
        self._url = a_url
    
    def _get_gems_data_gen(self):
        """
          Create the parser generator
        """
        print("get session id form gems\n")
        self._get_session_id()
        
        print("request GEMS logs\n")
        
        url = self._url
        
        while url:
        
            print("###### HTTP REQUEST ######\n")
            r = requests.get(url, cookies = self._cookies)
            
            print("###### PARSING ######\n")
            next_url   = GEMSHTMLParser.get_next_url(r.content)
            
            gems_lines = GEMSHTMLParser.get_GEMS_events(r.content)
            
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
        
    def extract(self):
        """
           Extract the information
        """
        
        print("get session id form gems\n")
        self._get_session_id()
        
        print("request GEMS logs\n")
        r = requests.get(GEMSExtractor.DATA_URL, cookies =self._cookies)
        
        return r.content


        
def get_text_value_from_node(a_node):     
    return   " ".join(t.nodeValue for t in a_node.childNodes if t.nodeType == t.TEXT_NODE)


def old_method_to_get_data():
    
    extractor = GEMSExtractor()
    
    content = extractor.extract()
    
    print(content)
    
    
    #parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"))

    #html_doc = parser.parse(content)
    
    doc = BeautifulSoup(content)
    
    data_table = doc.find('table', width='100%')
    
    for row in data_table.findAll('tr')[2:]:
        
        cols = row.findAll('td')
        
        if len(cols) == 6:
            ip       = cols[0].string
            facility = cols[1].string
            host     = cols[2].string
            agent    = cols[3].string
            lvl      = cols[4].string
            msg      = cols[5].string
            #print("msg = %s\n" %(msg))
        else:
            print("We have a problem \n")
            
    
    #look for a title='Next'
    #next = doc.findAll( (lambda tag: (tag.name == 'a' and tag.href.startswith('HistoryFilterRetry.jsp') if tag.href) ) )
    next = doc.find('a', href = re.compile('HistoryFilterDisplay\.jsp\?.*'))
    #(tag.href.startswith("HistoryFilterDisplay.jsp") if tag.href else False)))
    #print(next)
    if next:
        print("There is a next %s\n" % (next))
        for (n,v) in next.attrs:
            if n == 'href':
                print("next url %s\n" % (v))
    else:
        print("No next\n")
 
    
    """
    tables = doc.getElementsByTagName('table')
    
    #get first table
    table = tables[0]
    
    row_nb = 1
    
    for row in table.getElementsByTagName('tr'): 
        print("********* Row nb %d\n" % (row_nb)) 
        cols = row.getElementsByTagName('td')
        col_nb = 1
        
        if len(cols) == 6:
            ip       = get_text_value_from_node(cols[0])
            facility = get_text_value_from_node(cols[1])
            host     = get_text_value_from_node(cols[2])
            agent    = get_text_value_from_node(cols[3])
            lvl      = get_text_value_from_node(cols[4])
            msg      = get_text_value_from_node(cols[5])
            print("ip = %s, fac = %s, host = %s, agent = %s, lvl = %s, msg = %s\n" %(ip, facility, host, agent, lvl, msg))
        else:
            print("ignore here\n")
        
        row_nb += 1
      """
          
if __name__ == '__main__':
    
    gems_extractor = GEMSExtractor(start_time = "2011-10-12 15:11:00", end_time = "2011-10-12 15:14:00", severity = ["A","W","I"], facility = ['DVB_EUR_UPLINK'])
    
    cpt = 1
    for line in gems_extractor:
        if cpt < 10:
            print("%d,%s" %(cpt, line) )
        cpt += 1
    
    
    gems_extractor = GEMSExtractor(start_time = "11.308.15.02.03", end_time = "11.308.15.12.03", severity = ["A","W","I"], facility = ['DVB_EUR_UPLINK'])
    
    #gems_extractor.set_url_to_parse(GEMSExtractor.DATA_URL)
    
    cpt = 1
    for line in gems_extractor:
        if cpt < 5:
            print("%d,%s" %(cpt, line) )
        cpt += 1
    
        
    
    
    