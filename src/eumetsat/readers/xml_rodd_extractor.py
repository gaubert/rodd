'''
Created on 20 Jan 2011

@author: guillaume.aubert@eumtetsat.int
'''

from lxml import etree
import StringIO
import os
import eumetsat.common.utils as utils


UNDEFINED = "UNDEFINED"

def pprint_dict(a_dict, a_out, a_format="%-25s %s\n"):
    """ pretty print a dictionary """
    for (key, val) in a_dict.items():
        a_out.write(a_format % (str(key)+':', val))

class RoddExtractor(object):
    
    """ Generic Importer
    """
    DISCARD = ['FTP', 'EUMETSATWebsite', 'CMACast', 
               'SAF Archive & FTP', 'Internet', 'AVISO',
                'NOAA CLASS Archive', 'SAF' ]
                
    KEEP    = ['Direct', 'EUMETSAT Data Centre', 'GTS',
               'GEONETCast-Americas', 'EUMETCast' , 'EUMETCast-Africa',
               'EUMETCast-Europe', 'EUMETCast-Americas']
    
    def __init__(self, a_xml_directory):
        """ constructor """
        
        self._root_dir = a_xml_directory
        
    
    def read_table_products(self):
        """ Read the table product and 
        
        """
    
    def process_dir(self, dir):
        """ process all the files in a dir """
        for the_file in utils.dirwalk(dir):
            print("Parsing %s\n" %(os.path.basename(the_file)))
            self.read_xml(the_file)
        
        
    def read_xml(self, a_file_path):
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
        
        #dir  = "/homespace/gaubert/mdexport-run-3123635774208809095282646930287344/download-5709376852774485935282647175391973"
        
        #file_path = "/homespace/gaubert/mdexport-run-3123635774208809095282646930287344/download-5709376852774485935282647175391973/metadata_146.xml"
        
        ns = {          'gmd':'http://www.isotc211.org/2005/gmd',
                        'gco':'http://www.isotc211.org/2005/gco',
                        'gmi':'http://www.isotc211.org/2005/gmi',
                        'gml':'http://www.opengis.net/gml',
                        'xsi':'http://www.w3.org/2001/XMLSchema-instance',
                        'eum':'http://www.eumetsat.int/2008/gmi' }
        
    
        extracts = { 'distribution' : [] }
        doc = etree.parse(open(a_file_path,'r'))
       
        # get name
        res = doc.xpath("//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString", \
                        namespaces= ns)
        if len(res) > 0:
            extracts['name'] = res[0].text
        else:
            extracts['name'] = UNDEFINED
        
        #get unique id
        res = doc.xpath("//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code/gco:CharacterString", \
                         namespaces = ns)
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
    
                # get the availablity elements
                for child in elem.iter("{%s}availability"% (ns['eum']) ):
                    val = child.find("{%s}CharacterString" % (ns['gco']))
                    if val is not None:
                        #print("%s - %s" % (val.tag, val.text))
                        # discard it when it is EUMETSATWebsite
                        distribution = val.text
                        if distribution.strip() in RoddExtractor.DISCARD:
                            print("xx DISCARD %s for %s\n" %( distribution, os.path.basename(a_file_path)))
                        else:
                            if 'EUMETCast' in distribution:
                                list_of_dist = distribution.split(',')
                                if 'EUMETCast' in list_of_dist:
                                    list_of_dist.remove('EUMETCast')
                                extracts['distribution'].extend(list_of_dist)
                            else:
                                if distribution in RoddExtractor.KEEP:
                                    extracts['distribution'].append(distribution)
                                else:
                                    print("******** %s not in KEEP for %s\n" %(distribution, os.path.basename(a_file_path)))
                                    
                #get the formats elements
                # create the file part for each part
                                    
        else:
            print("WARN: No distribution info for %s. Probably an external product\n" %(os.path.basename(a_file_path)))
            return
        
        out = StringIO.StringIO()
        pprint_dict(extracts, out)
        print("== File %s = \n%s\n" %(os.path.basename(a_file_path), out.getvalue()))
        
        
            
if __name__ == "__main__":
    
    dir = "/homespace/gaubert/mdexport-run-3123635774208809095282646930287344/download-5709376852774485935282647175391973"
    
    extractor = RoddExtractor("MyExtrractorDir")
    extractor.process_dir(dir)
    #extractor.read_xml("%s/%s" %(dir, 'metadata_89.xml'))