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
    """
       check matcher
    """
    context =  { 'gmi': "http://www.isotc211.org/2005/gmi",
                 'eum': "http://www.eumetsat.int/2008/gmi",
                 'gco': "http://www.isotc211.org/2005/gco",
                 'gmd': "http://www.isotc211.org/2005/gmd",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance"
               }
    
    for the_file in fs.dirwalk('/homespace/gaubert/RODD/src-data/130810-vprodnav/',"*.xml"):
        
        print("file = %s\n" % (the_file))
        doc = xml.dom.minidom.parse(the_file).documentElement
    
        lid = xpath.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=context)
        print("[id:%s , path:%s]\n" % (lid[0], the_file))
        
        lid = xpath.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=context)
        print("[id:%s , path:%s]\n" % (lid[0], the_file))
        

def _gn_with(names, a_nodes_list):
    """ internal recursive function """
    
    # stopping case
    if len(names) == 0:
        return a_nodes_list
    
    res = []
    for the_elem in a_nodes_list:
        #print("names[0] = %s ; the_elem.localName = %s\n" %(names[0], the_elem.localName))
        if the_elem.nodeType == the_elem.ELEMENT_NODE and the_elem.localName == names[0]:
            
            # last so return the element
            if len(names) == 1:
                res.append(the_elem)
            else:
                #recurse again
                res.extend(_gn_with(names[1:], the_elem.childNodes))
    
    return res
    
   
def get_nodes_with(a_localNamePath, a_childNodes):
    """ 
        dummy xpath using minidom 
    """
    
    names = a_localNamePath.split('/')
    
    #remove first line for the case where there is a / first
    if names[0] == '':
        names = names[1:]
    
    return _gn_with(names, a_childNodes)
    
def contains(a_str, a_to_find, a_case_insensitive = True):
    """
       Check if a string contains the passed strings
    """
    for elem in a_to_find:
        if a_case_insensitive:
            if a_str.lower().find(elem.lower()) != -1:
                return True
        else:
            if a_str.find(elem) != -1:
                return True  
    
    return False
    
def print_filetype_tree():
    """
       Print all filetypes as a tree
    """
    context =  { 'gmi': "http://www.isotc211.org/2005/gmi",
                'eum': "http://www.eumetsat.int/2008/gmi",
                'gco': "http://www.isotc211.org/2005/gco",
                'gmd': "http://www.isotc211.org/2005/gmd",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance"
              }
    
    out = StringIO.StringIO()
    filtered = StringIO.StringIO()
    
    different_availabilities = set()
    
    for file in fs.dirwalk('/homespace/gaubert/RODD/src-data/130810-vprodnav/',"*.xml"):
        
        #print("file = %s\n" % (file))
        doc = xml.dom.minidom.parse(file).documentElement
        #doc = elementtree.ElementTree.parse(file)
        
        fileidentifier   = xpath.findvalues('/gmi:MI_Metadata/gmd:fileIdentifier/gco:CharacterString', doc, namespaces=context)

        #out.write("+-%s:%s\n" % (fileidentifier[0], os.path.basename(file)))
        filename_written = False

        digitaltransfers = xpath.find('//eum:digitalTransfers/eum:MD_EUMDigitalTransfer', doc, namespaces=context)
        
        for elem in digitaltransfers:
            
            #get availability value
            list_of_elems = get_nodes_with("/availability/MD_EUMDigitalTransferOptions/availability/CharacterString", elem.childNodes)
            
            if len(list_of_elems) > 1:
                raise Exception("Error too many elements found")
            
            availability_type = " ".join(t.nodeValue for t in list_of_elems[0].childNodes if t.nodeType == t.TEXT_NODE)
            different_availabilities.add(availability_type.strip())
            
            # get list of channels
            list_of_channels = get_nodes_with("/availability/MD_EUMDigitalTransferOptions/eumetcastChannels/CharacterString", elem.childNodes)
            chans = ""
            for ch in list_of_channels:
                chans += " ".join(t.nodeValue for t in ch.childNodes if t.nodeType == t.TEXT_NODE)
            #print("chans = %s\n" %(chans))
            if contains(availability_type, ['EUMETCAST','GTS','DIRECT']): 
                
                #write name
                if not filename_written:
                    out.write("+-%s:%s:ch=[%s]\n" % (fileidentifier[0], os.path.basename(file),chans))
                    filename_written = False
                    
                # get associated formats to this type
                #if contains(availability_type,["EUMETCAST","GEONETCAST", ] ):
                format_list = get_nodes_with("/format/MD_EUMFormat", elem.childNodes)
                
                for e in format_list:
                    
                    dummy_list = get_nodes_with("/name/CharacterString", e.childNodes)
                    
                    dum_node = dummy_list[0]
                    name = " ".join(t.nodeValue for t in dum_node.childNodes if t.nodeType == t.TEXT_NODE)
                    
                    dummy_list = get_nodes_with("/typicalFilename/CharacterString", e.childNodes)
                    
                    typicalfilenames = []
                    for dum_node in dummy_list:
                        typicalfilenames.append(" ".join(t.nodeValue for t in dum_node.childNodes if t.nodeType == t.TEXT_NODE))
                    
                    out.write(" \__(%s:%s)\n" % (availability_type, name.strip()) )
                    for n in typicalfilenames:
                        out.write("     \__%s\n" % (n.strip()))
            else:
                
                #write name
                if not filename_written:
                    filtered.write("+-%s:%s\n" % (fileidentifier[0], os.path.basename(file)))
                    filename_written = False
                    
                # get associated formats to this type
                #if contains(availability_type,["EUMETCAST","GEONETCAST", ] ):
                format_list = get_nodes_with("/format/MD_EUMFormat", elem.childNodes)
                
                for e in format_list:
                    
                    dummy_list = get_nodes_with("/name/CharacterString", e.childNodes)
                    
                    dum_node = dummy_list[0]
                    name = " ".join(t.nodeValue for t in dum_node.childNodes if t.nodeType == t.TEXT_NODE)
                    
                    dummy_list = get_nodes_with("/typicalFilename/CharacterString", e.childNodes)
                    
                    typicalfilenames = []
                    for dum_node in dummy_list:
                        typicalfilenames.append(" ".join(t.nodeValue for t in dum_node.childNodes if t.nodeType == t.TEXT_NODE))
                    
                    filtered.write(" \__(%s:%s)\n" % (availability_type, name.strip()) )
                    for n in typicalfilenames:
                        filtered.write("     \__%s\n" % (n.strip()))
                    
                #print("name = %s ; filesnames = %s\n" % (name, typicalfilenames) )
            
            
         
    #print(out.getvalue())
    out.write("-------------------------------------------------------------------\n")
    out.write("Availabilities type:\n")
    for av in different_availabilities:
        out.write("- %s\n" % av)
    o_file= open("/tmp/dissemination-tree.txt", "w")
    o_file.write(out.getvalue())
    o_file.close() 
    
    o_file= open("/tmp/filtered-tree.txt", "w")
    o_file.write(filtered.getvalue())
    o_file.close() 
    
               

if __name__ == '__main__':
    print_filetype_tree()