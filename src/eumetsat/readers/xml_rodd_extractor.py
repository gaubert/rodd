'''
Created on 20 Jan 2011

@author: guillaume.aubert@eumtetsat.int
'''

from lxml import etree
import StringIO


UNDEFINED = "UNDEFINED"

def pprint_dict(a_dict, a_out, a_format="%-25s %s\n"):
    """ pretty print a dictionary """
    for (key, val) in a_dict.items():
        a_out.write(a_format % (str(key)+':', val))

class RoddExtractor(object):
    
    """ Generic Importer
    """
    
    def __init__(self, a_xml_directory):
        """ constructor """
        
        self._root_dir = a_xml_directory
        
    
    def read_table_products(self):
        """ Read the table product and 
        
        """
        
        
    def read_xml(self):
        """ read_xml file.
            
            return the default if it is not found and if fail_if_missing is False, otherwise return NoOptionError
          
            :param section: Section where to find the option
            :type  section: str
            :param option:  Option to get
            :param default: Default value to return if fail_if_missing is False
            :param fail_if_missing: Will throw an exception when the option is not found and fail_if_missing is true
               
            :returns: the option as a string
            
            :except NoOptionError: Raised only when fail_is_missing set to True
            
        """
        
        dir  = "/homespace/gaubert/mdexport-run-3123635774208809095282646930287344/download-5709376852774485935282647175391973"
        
        file_path = "/homespace/gaubert/mdexport-run-3123635774208809095282646930287344/download-5709376852774485935282647175391973/metadata_146.xml"
        
        ns = {          'gmd':'http://www.isotc211.org/2005/gmd',
                        'gco':'http://www.isotc211.org/2005/gco',
                        'gmi':'http://www.isotc211.org/2005/gmi',
                        'gml':'http://www.opengis.net/gml',
                        'xsi':'http://www.w3.org/2001/XMLSchema-instance',
                        'eum':'http://www.eumetsat.int/2008/gmi' }
        
    
        extracts = { 'distribution' : [] }
        doc = etree.parse(open(file_path,'r'))
       
        # get name
        res = doc.xpath("//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString", namespaces= ns)
        if len(res) > 0:
           extracts['name'] = res[0].text
        else:
           extracts['name'] = UNDEFINED
        
        #get unique id
        res = doc.xpath("//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString", namespaces= ns)
        if len(res) > 0:
           extracts['uid'] = res[0].text
        else:
           extracts['uid'] = UNDEFINED
        
        #get description
        res = doc.xpath("//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString", namespaces = ns)
        if len(res) > 0:
           extracts['description'] = res[0].text
        else:
           extracts['description'] = UNDEFINED
        
        #get distribution info
        
        # start to get all the eum:MD_EUMDigitalTransferOptions
        res = doc.xpath("//eum:MD_EUMDigitalTransferOptions", namespaces = ns)
        if len(res) > 0:
            for elem in res:
                # look for internal element
                elem.find('{%s}availability'%(ns['eum']))
                
                print("Elem ========\n")
                #tag=etree.Element
                for child in elem.iter("{%s}availability"% (ns['eum']) ):
                    val = child.find("{%s}CharacterString" % (ns['gco']))
                    if val is not None:
                        print("%s - %s" % (val.tag, val.text))
                        extracts['distribution'] = val.text
                        
        else:
            raise Exception("Error")
        
        out = StringIO.StringIO()
        pprint_dict(extracts, out)
        print("Extracts = \n%s\n" %(out.getvalue()))
        
        
            
if __name__ == "__main__":
    
    extractor = RoddExtractor("MyExtrractorDir")
    extractor.read_xml()    