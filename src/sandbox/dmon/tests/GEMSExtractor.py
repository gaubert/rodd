'''
Created on Nov 4, 2011

@author: guillaume.aubert@eumetsat.int
'''
import requests
import html5lib

class GEMSExtractor(object):
    '''
       Extract Event from GEMS
    '''

    #used to get a JSESSIONID
    START_URL = 'http://omasif/GEMS/HistoryFilterRetry.jsp?startTime=11.308.15.02.03&endTime=11.308.15.12.03&severity=A&severity=W&severity=I&facility=DVB_EUR_UPLINK'
    
    # to access the data
    DATA_URL  = 'http://omasif/GEMS/HistoryFilterController.jsp?startTime=11.307.15.02.03&severity=A&endTime=11.308.15.12.03&severity=W&severity=I&facility=DVB_EUR_UPLINK&host=&process=&search=&pageSize=4&x=50&y=6'

    def __init__(self):
        '''
        Constructor
        '''
        self._cookies = None
    
    def _get_session_id(self):
        """
          get the session id that is necessary to get to browse GEMS
        """
        r = requests.get(GEMSExtractor.START_URL)
        self._cookies = r.cookies
        
    def extract(self):
        """
           Extract the information
        """
        
        self._get_session_id()
        
        r = requests.get(GEMSExtractor.DATA_URL, cookies =self._cookies)
        
        return r.content
        
def get_text_value_from_node(a_node):     
    return   " ".join(t.nodeValue for t in a_node.childNodes if t.nodeType == t.TEXT_NODE)


if __name__ == '__main__':
    
    extractor = GEMSExtractor()
    
    content = extractor.extract()
    
    #print(content)
    parser = html5lib.HTMLParser(tree=html5lib.treebuilders.getTreeBuilder("dom"))

    doc = parser.parse(content)
    
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
        
        """for col in cols:
            print("--------- Col nb %d \n" % (col_nb))
            print " ".join(t.nodeValue for t in col.childNodes if t.nodeType == t.TEXT_NODE)
            col_nb += 1
        """
        
        row_nb += 1
    
    
    