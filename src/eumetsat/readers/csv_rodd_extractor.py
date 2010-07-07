'''
Created on 7 Jul 2010

@author: guillaume.aubert@eumetsat.int
'''

import csv

class Lookup(dict):
    """
    a dictionary which can lookup value by key, or keys by value
    """
    def __init__(self, items=[]):
        """items can be a list of pair_lists or a dictionary"""
        dict.__init__(self, items)
 
    def get_key(self, value):
        """find the key(s) as a list given a value"""
        return [item[0] for item in self.items() if item[1] == value]
 
    def get_value(self, key):
        """find the value given a key"""
        return self[key]

class RoddExtractor(object):
    
    """ Generic Importer
    """
    # dict to map rodd column name with the mysql column names
    PRODUCT_MAPPER = { 
                      "title"                  : "title",
                      "EUMETCast"              : "onEumetcast",
                      "MSGDirect"              : "onMsgDirect",
                      "GTS"                    : "onGts",
                      "General_Comments"       : "generalComments",
                      #"usingen_login"          : "",
                      #"PN_db_comments"         : "",
                      "InternalID"             : "internalID",
                      "acr"                    : "acronym",
                      #"transfer_method"        : "",
                      "aka"                    : "aka",
                      "source"                 : "source",
                      "category"               : "category",
                      "channel"                : "channel",
                      "descKeyword_discipline" : "descKeywordDiscipline",
                      "descKeyword_place"      : "desKeywordPlace",
                      "dissemination"          : "dissemination",
                      #"msg_direct"             : "",
                      "hrpt_direct"            : "hrpt_dir",
                      "filesize"               : "filesize",
                      "OICD"                   : "oicd",
                      "formats"                : "formats",
                      "frequency"              : "frequency",
                      "instrument"             : "instrument",
                      "link_1"                 : "link",
                      "regular_expression"     : "regularExpr",
                      "namingconvention"       : "namingConvention",
                      "orbitType"              : "orbitType",
                      "parameter"              : "parameter",
                      "provider"               : "provider",
                      "refFile"                : "referenceFile",
                      "resolution"             : "resolution",
                      "resources_1"            : "resources",
                      #"person"                 : "",
                      "sat"                    : "satellite",
                      "status"                 : "status"
                     }  
    
    PRODUCT_TABLE_ORDER = ["title", "onEumetcast", "onGts", "onMsgDirect", "generalComments", "internalID", "acronym", "aka", "source", "category", "channel", "descKeywordDiscipline", "descKeywordPlace", "dissemination", "hrpt_dir", "filesize", "oicd", "formats", "frequency", "instrument", "link", "regularExpr", "namingConvention", "orbitType", "parameter", "provider", "referenceFile", "resolution", "resources", "satellite", "status" ]

    
    
    def __init__(self, a_directory):
        """ constructor """
        
        self._root_dir = a_directory
    
    def read_csv_and_create_sql(self):
        """ read csv product table """
        
        csv_reader = csv.DictReader(open('/cygdrive/d/RODD-Copy/tbl_Products.csv'))
        
        cpt = 0
        
        
        for row in csv_reader:
            print('Row %d = [%s]' %(cpt,row) )
            cpt += 1