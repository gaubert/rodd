'''
Created on Feb 14, 2014

@author: gaubert
'''
import re
import eumetsat.dmon.gems_feeder as gems_feeder

"GTS headers of outgoing file W_XX-EUMETSAT-Darmstadt,SOUNDING+SATELLITE,METOPB+GRAS_C_EUMP_20140211232028_07278_eps_o_thn_l1.bin: IEGX01 EUMP 112316; IEGX01 EUMP 112318; IEGX01 EUMP 112319;"

#process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 

process_expr = "GTS headers of outgoing file (?P<file>.*): (?P<bulletins>.*)"
expr_re = re.compile(process_expr)

if __name__ == '__main__':
    
    #fd = open("/Users/gaubert/OneDayOfRMDCNOugoingHeaders.htm")
    fd = open("/Users/gaubert/simple_bull.html")
    
    htmlStr = ""
    
    for line in fd.readlines():
        htmlStr += line
    
    events = gems_feeder.GEMSHTMLParser.get_GEMS_events(htmlStr)
    
    for ev in events:
        print("Event: msg %s\n" % (ev['msg']))
        
        matched = expr_re.match(ev['msg'])
        if matched:     
            filename  = matched.group('file')
            bulletins = matched.group('bulletins')
            print("filename = %s, bulletins = %s\n" % (filename, bulletins))
    

