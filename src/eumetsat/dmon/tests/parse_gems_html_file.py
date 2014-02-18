'''
Created on Feb 14, 2014

@author: gaubert
'''
import re
import eumetsat.dmon.gems_feeder as gems_feeder

"GTS headers of outgoing file W_XX-EUMETSAT-Darmstadt,SOUNDING+SATELLITE,METOPB+GRAS_C_EUMP_20140211232028_07278_eps_o_thn_l1.bin: IEGX01 EUMP 112316; IEGX01 EUMP 112318; IEGX01 EUMP 112319;"

#process_expr = "\(('|\")(?P<line>.*)('|\"),\s('|\")(?P<filename>.*)('|\")\)" 

line_expr = "[\t, ]*<td>GTS headers of outgoing file (?P<file>.*): (?P<bulletins>.*)</td>"
line_re = re.compile(line_expr)

process_expr = "GTS headers of outgoing file (?P<file>.*): (?P<bulletins>.*)"
expr_re = re.compile(process_expr)

if __name__ == '__main__':
    
    fd = open("/Users/gaubert/OneDayOfRMDCNOugoingHeaders.htm")
    #fd = open("/Users/gaubert/simple_bull.html")
    
    res_fd = open("/Users/gaubert/result.csv", "w+")
    
    htmlStr = ""
    
    for line in fd.readlines():
        if "<td>GTS headers" in line:
            print("We are in \n")
        matched = line_re.match(line)
        if matched:     
            filename  = matched.group('file')
            bulletins = matched.group('bulletins')
            bull_str = bulletins.split(";")
            bull_info = []
            unique_bull = []
            res_line = "%s" % (filename)
            for bull in bull_str:
                b_info = bull.strip().split(" ")
                if len(b_info)>=2:
                    #b1 = b_info[0]
                    #b2 = b_info[1]
                    if b_info[0] not in unique_bull:
                        unique_bull.append(b_info[0])
                        bull_info.append( (b_info[0], b_info[1]) )
                        res_line += ",%s:%s" % (b_info[0], b_info[1])
            print("filename = %s,\n bull_info = %s\n" % (filename, bull_info))
            res_line += "\n"
            res_fd.write(res_line)
    
    #for line in fd.readlines():
    #    htmlStr += line
    
    #events = gems_feeder.GEMSHTMLParser.get_GEMS_events(htmlStr)
    
    #for ev in events:
    #    print("Event: msg %s\n" % (ev['msg']))
        
    #    matched = expr_re.match(ev['msg'])
    #    if matched:     
    #        filename  = matched.group('file')
    #        bulletins = matched.group('bulletins')
    #        print("filename = %s, bulletins = %s\n" % (filename, bulletins))
    

