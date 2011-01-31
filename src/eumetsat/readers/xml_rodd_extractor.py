'''
Created on 20 Jan 2011

@author: guillaume.aubert@eumtetsat.int
'''

from lxml import etree
import StringIO
import os
import sys
from eumetsat.common.collections import OrderedDict
import eumetsat.common.utils as utils
import simplejson


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
    
    DIS_TRANSLATION = {
                        "Direct" : "direct-info",
                        "EUMETSAT Data Centre" : "data-centre-info",
                        "GTS" : "gts-info",
                        "GEONETCast-Americas" : "geonetcast-info",
                        "EUMETCast" : "eumetcast-info",
                        'EUMETCast-Africa' : "eumetcast-info",
                        "EUMETCast-Europe" : "eumetcast-info",
                        "EUMETCast-Americas" : "eumetcast-info"
                       }
    
    def __init__(self, a_xml_directory):
        """ constructor """
        
        self._root_dir = a_xml_directory
        
    
    def read_table_products(self):
        """ Read the table product and 
        
        """
    
    def process_dir(self, dir):
        """ process all the files in a dir """
        
        all_products = {
                         "products" : []
                       }
        
        for the_file in utils.dirwalk(dir):
            print("Parsing %s\n" %(os.path.basename(the_file)))
            prod_dir = self.read_xml(the_file)  
            if prod_dir and len(prod_dir.items()) > 1:
                all_products["products"].append(prod_dir)
        
        simplejson.dump(all_products,open("/tmp/all_products.json","w"),sort_keys=False, indent=True)
            
        
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
        
    
        extracts = OrderedDict()
        extracts['filename'] = os.path.basename(a_file_path)
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
            dummy_l = extracts['uid'].split(":")
            
            # Do not include Software packages in RODD only products
            if (dummy_l[2] == "SW") or (dummy_l[2] == "DOC"):
                print("**************** Ignore %s because it isn't a product\n" %(extracts['uid']))
                return None
                
            
            # create the filename prefix (remove eumetcast beginning)
            filename_prefix = "_".join(dummy_l[3:])
        else:
            extracts['uid'] = UNDEFINED
        
        #get description
        res = doc.xpath("//gmd:identificationInfo/gmd:MD_DataIdentification/gmd:abstract/gco:CharacterString", namespaces = ns)
        if len(res) > 0:
            extracts['description'] = res[0].text
        else:
            extracts['description'] = UNDEFINED
        
        #get distribution info
        extracts['distribution'] = []
        
        # start to get all the eum:MD_EUMDigitalTransfer
        res = doc.xpath("//eum:MD_EUMDigitalTransfer", namespaces = ns)
        if len(res) > 0:
            i = 0
            for transfer in res:
                dummy_dists = []
                # get eum:MD_EUMDigitalTransfersOptions and extract the distribution info from it
                transfer_option = transfer.find("{%s}availability/{%s}MD_EUMDigitalTransferOptions" % (ns['eum'], ns['eum'])) 
                
                for elem in transfer_option:
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
                                    # use a set to remove the different eumetcast values for the moment
                                    dummy_dists = set([RoddExtractor.DIS_TRANSLATION[elem] for elem in list_of_dist])
                                    extracts['distribution'].extend(dummy_dists)
                                else:
                                    if distribution in RoddExtractor.KEEP:
                                        dummy_dists.append(RoddExtractor.DIS_TRANSLATION[distribution])
                                        extracts['distribution'].append(RoddExtractor.DIS_TRANSLATION[distribution])
                                    else:
                                        print("******** %s not in KEEP for %s\n" %(distribution, os.path.basename(a_file_path)))
                
                # get eum:format for the current distributions
                xml_elem = transfer.find("{%s}format/{%s}MD_EUMFormat/{%s}name/{%s}CharacterString" % (ns['eum'], ns['eum'], ns['gmd'], ns['gco']) )
                if xml_elem != None:
                    type_name = xml_elem.text if xml_elem.text else ""
                    print("type_name = [%s]\n" % (type_name))     
                
                #get typicalFilename to build the regexpr
                typical_fn_list = transfer.findall("{%s}format/{%s}MD_EUMFormat/{%s}typicalFilename/{%s}CharacterString" % (ns['eum'], ns['eum'], ns['eum'],  ns['gco']) )
                reg_exprs = ""
                if len(typical_fn_list) > 0:
                    reg_expr_nb = 0
                    for filen in typical_fn_list:
                        reg_exprs += "(%s)" % (filen.text) if reg_expr_nb == 0 else "|(%s)" % (filen.text)
                        reg_expr_nb += 1
                        
                           
                           
                for dist in dummy_dists:
                    if not extracts.get(dist, None):
                        extracts[dist] = { "files": [
                                                    ]}
                    
                    if (len(type_name.strip()) > 0) or (len(reg_exprs) > 0):
                        extracts[dist]["files"].append( { 
                                                          "name"     : '%s_%d' % (filename_prefix.lower(),i),
                                                          "type"     : type_name,
                                                          "regexpr"  : reg_exprs,
                                                          "dis_type" : [dist]
                                                        })  
                        i += 1
                    
        else:
            print("WARN: No distribution info for %s. Probably an external product\n" %(os.path.basename(a_file_path)))
            return extracts
        
        out = StringIO.StringIO()
        pprint_dict(extracts, out)
        print("== File %s = \n%s\n" %(os.path.basename(a_file_path), out.getvalue()))
        return extracts
        
            
if __name__ == "__main__":
    
    dir = "/homespace/gaubert/mdexport-run-3123635774208809095282646930287344/download-5709376852774485935282647175391973"
    
    extractor = RoddExtractor("MyExtrractorDir")
    extractor.process_dir(dir)
    #extractor.read_xml("%s/%s" %(dir, 'metadata_89.xml'))