'''
Created on 25 Jun 2010

@author: guillaume.aubert@eumtetsat.int
'''
from xml.etree.ElementTree import ElementTree

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
        tree = ElementTree()
        
        tree.parse("H:/Dev/ecli-workspace/rodd/etc/data/rodd-data/tbl_Products.xml")
        
        iter = tree.getiterator("tbl_Products")
        
        cpt=1
        
        for node in iter:
            
            print("\n--- Node %s, nb %s\n" % (node.tag, cpt) )
            
            if node.getchildren():
                for child in node:
                    print("    %s = %s" %(child.tag, child.text) )
