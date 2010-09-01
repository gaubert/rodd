'''
Created on Aug 13, 2010

@author: guillaume.aubert@eumetsat.int
'''

import xml.dom.minidom
import xpath
import eumetsat.common.filesystem_utils as fs
import elementtree.ElementTree
import os
import StringIO



def run_test():
        doc = xml.dom.minidom.parse('/homespace/gaubert/RODD/src-data/130810-vprodnav/3.xml').documentElement
        
        # create context
        context = xpath.XPathContext()
        
        c = { 'gmi': "http://www.isotc211.org/2005/gmi",
              'eum': "http://www.eumetsat.int/2008/gmi",
              'gco': "http://www.isotc211.org/2005/gco",
              'gmd': "http://www.isotc211.org/2005/gmd",
              "xsi": "http://www.w3.org/2001/XMLSchema-instance"
            }
        
        context.namespaces['gmi'] = "http://www.isotc211.org/2005/gmi"
        context.namespaces['eum'] = "http://www.eumetsat.int/2008/gmi"
        context.namespaces['gco'] = "http://www.isotc211.org/2005/gco"
        context.namespaces['gmd'] = "http://www.isotc211.org/2005/gmd"
        context.namespaces['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        

        
        #result = xpath.find('gmd:MD_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=c)
        result = xpath.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=c)
        print("Result = %s\n" % (result))
        
        result = context.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=c)
        print("Result = %s\n" % (result))
        

def run_matcher():
    
    context =  { 'gmi': "http://www.isotc211.org/2005/gmi",
                 'eum': "http://www.eumetsat.int/2008/gmi",
                 'gco': "http://www.isotc211.org/2005/gco",
                 'gmd': "http://www.isotc211.org/2005/gmd",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance"
               }
    
    for file in fs.dirwalk('/homespace/gaubert/RODD/src-data/130810-vprodnav/',"*.xml"):
        
        print("file = %s\n" % (file))
        doc = xml.dom.minidom.parse(file).documentElement
    
        lid = xpath.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=context)
        print("[id:%s , path:%s]\n" % (lid[0], file))
        
        lid = xpath.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=context)
        print("[id:%s , path:%s]\n" % (lid[0], file))
        

def get_nodes_with(a_localName, a_childNodes):
    """"""
    res = []
    for the_elem in a_childNodes:
        if the_elem.nodeType == the_elem.ELEMENT_NODE and the_elem.localName == a_localName:
            res.append(the_elem)
    
    return res
    

    
def print_filetype_tree():
    
     context =  { 'gmi': "http://www.isotc211.org/2005/gmi",
                 'eum': "http://www.eumetsat.int/2008/gmi",
                 'gco': "http://www.isotc211.org/2005/gco",
                 'gmd': "http://www.isotc211.org/2005/gmd",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance"
               }
     
     out = StringIO.StringIO()
     out = open("/tmp/res.txt","w")
     
     for file in fs.dirwalk('/homespace/gaubert/RODD/src-data/130810-vprodnav/',"*.xml"):
        
        #print("file = %s\n" % (file))
        doc = xml.dom.minidom.parse(file).documentElement
        #doc = elementtree.ElementTree.parse(file)
        
        fileidentifier   = xpath.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=context)

        out.write("+-%s:%s\n" % (fileidentifier[0], os.path.basename(file)))

        formatsnodes =   xpath.find('//eum:format/eum:MD_EUMFormat', doc, namespaces=context)
        
        for elem in formatsnodes:
            #first get name
            for e in get_nodes_with("name",elem.childNodes):
                for e1 in get_nodes_with("CharacterString",e.childNodes):
                    res = " ".join(t.nodeValue for t in e1.childNodes if t.nodeType == t.TEXT_NODE)
                    out.write(" \__%s\n" % (res.strip()) )
                    break
            
            # get typicalfilenames
            for e in elem.childNodes:
                if e.nodeType == e.ELEMENT_NODE and e.localName == "typicalFilename":
                    for e1 in e.childNodes:
                        if e1.nodeType == e1.ELEMENT_NODE and e1.localName == "CharacterString":
                            res = " ".join(t.nodeValue for t in e1.childNodes if t.nodeType == t.TEXT_NODE)
                            out.write("     \__%s\n" % (res.strip()) )
                            
           
           
     #print(out.getvalue())
     out.close()             

if __name__ == '__main__':
    print_filetype_tree()