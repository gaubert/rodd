'''
Created on Feb 14, 2014

@author: gaubert
'''
import eumetsat.dmon.gems_feeder as gems_feeder


if __name__ == '__main__':
    
    fd = open("/Users/gaubert/OneDayOfRMDCNOugoingHeaders.htm")
    
    htmlStr = ""
    
    for line in fd.readline():
        htmlStr += line
    
    gems_feeder.GEMSHTMLParser.get_GEMS_events(htmlStr)

