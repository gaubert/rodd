'''
Created on Aug 24, 2010

@author: guillaume.aubert@eumetsat.int
'''
import csv
import sqlalchemy

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

class LCSVRoddExtractor(object):
    '''
     Extract Data from the previous RODD DB
    '''
    
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
                      "descKeyword_place"      : "descKeywordPlace",
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

    LIGHT_PRODUCT_TABLE_COLS = ["title", "internalID", "regularExpr"]
    
    def __init__(self, a_directory, a_db_url):
        """ constructor """
        
        self._root_dir = a_directory
        
        self._db_url = a_db_url
        
        self._engine  = sqlalchemy.create_engine(self._db_url)
        
        self._conn    = self._engine.connect()
        
        # create MetaData 
        self._metadata      = sqlalchemy.MetaData()

        # bind to an engine
        # need to be binded to the engine now as the tables 
        # will use the reflection mechanism to be populated
        self._metadata.bind = self._engine
        
        self._schema      = "RODD"
        
    def _create_sql_columns(self, a_list):
        
        result = ""
        
        cpt = 0
        for elem in a_list:
            if cpt == 0:
                result += "%s" % (elem)
            else:
                result += ", %s" %(elem)
            cpt += 1

        return result
    
    def _transform_product_table_data(self,a_elem, a_value):
        """ Do the transformations for the product table """
        
        has_changed = False
        
        #print("Elem = %s\n" %(a_elem))
        
        if a_elem.startswith("on") or a_elem == 'hrpt_dir':
            if a_value == 'Y':
                a_value = "TRUE"
                has_changed = True
            else:
                a_value = "FALSE"  
                has_changed = True
        elif a_elem == 'link_1' or a_elem == 'resources':
            if "%" in a_value:
                a_value = "'%s'" % (a_value.replace("%", "%%"))
                has_changed = True
        
        return has_changed, a_value

    def clean_table(self,a_schema, a_table):
        
        result = self._conn.execute("delete from %s.%s;" %(a_schema, a_table))
    
    def read_csv_and_insert_product_sql(self, a_columns):
        """ 
           read csv product table 
           
           :param a_columns: list of colums to import
           :type  a_columns: str
        
           :returns: None
            
           :except Exception: if the content cannot be imported
        
        """
        
        csv_reader = csv.DictReader(open('%s/tbl_products.csv' %(self._root_dir)))
        
        nb_rows = 0
        
        lookup_dict = Lookup(LCSVRoddExtractor.PRODUCT_MAPPER)
        
        # for each line of data create an insert line

        insert_line = "INSERT INTO %s.%s (%s) VALUES (%s)"
        
        
        columns = self._create_sql_columns(a_columns)
        
        #file = open("/tmp/insert_products.sql","w+")

        for row in csv_reader:
            cpt_keys    = 0
            values      = ""
            has_changed = False
            
            for elem in a_columns:
                
                #get list of matching keys
                key = lookup_dict.get_key(elem)
                
                if not key:
                    raise Exception("Error: %s as no matching keys in %s" %(elem, LCSVRoddExtractor.PRODUCT_MAPPER))
                
                val = row.get(key[0], None)
                
                # and elem == "resources_1"
                if nb_rows == 200 and ("%" in val):
                    print("This is the break")
                
                has_changed, val = self._transform_product_table_data(elem, val)
                
                
                
                # if no transformations performed apply the standard rule taht considers the value as a string
                if has_changed:
                    val = val if val else "null"
                else:
                    val = "%s" % ( "'%s'" % (val) if val else "NULL")
                    
                # add in values
                if cpt_keys == 0:
                    values += "%s" % ( val )
                else:
                    values += ", %s" % ( val )
                
    
                cpt_keys += 1
                
            insert = insert_line %("RODD", "products", columns, values)
            
            print('[r%d]:insert = %s\n' %(nb_rows, insert) )
            #file.write("%s;\n" %(insert))
            result = self._conn.execute("%s;" %(insert))
            
            nb_rows += 1
        
    def read_csv_and_create_product_format_sql(self):
        """ read csv product table """
        
        pass
