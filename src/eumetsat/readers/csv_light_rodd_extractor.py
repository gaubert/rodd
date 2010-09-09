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
    
    PRODUCT_TABLE_ORDER = ["title", "onEumetcast", "onGts", "onMsgDirect", "generalComments", 
                           "internalID", "acronym", "aka", "source", "category", "channel", 
                           "descKeywordDiscipline", "descKeywordPlace", "dissemination", 
                           "hrpt_dir", "filesize", "oicd", "formats", "frequency", "instrument", 
                           "link", "regularExpr", "namingConvention", "orbitType", "parameter", 
                           "provider", "referenceFile", "resolution", "resources", "satellite", "status" ]

    LIGHT_PRODUCT_TABLE_COLS = ["title", "internalID", "regularExpr"]
    
    # mapping csv to mysql table
    CHANNEL_MAPPER = {
                      "channel"           : "name",
                      "PID_EB9"           : "pidEB9",
                      "PID_AB3"           : "pidAB3",
                      "PID_NSS"           : "pidNSS",
                      "multicast_address" : "multicastAddress",
                      "min_rate"          : "minRate",
                      "max_rate"          : "maxRate",
                      "channel_function"  : "channelFunction"
                     }
    
    CHANNEL_TABLE_COLS = ["name", "multicastAddress", "minRate", "maxRate", "channelFunction", "pidEB9", "pidAB3", "pidNSS"]
    
    SERVICE_MAPPER = {
                      "serviceID"          : "servID",
                      "service_directory"  : "name",
                      "channel"            : "chanID"
                     }

    SERVICE_COLS   = ["servID", "name", "chanID"]
    
    PROD2SERV_MAPPER = {
                         "RODDID"     : "roddID",
                         "serviceID"  : "servID",
                       }
    
    PROD2SERV_COLS  = [ "roddID" , "servID" ]
    
    FAMILIES_MAPPER = {
                         "familyID"     : "famID",
                         "family"       : "name",
                         "display_name" : "description"
                       }
    
    FAMILIES_COLS  = [ "famID" , "name", "description" ]
    
    SERV2FAMILY_MAPPER = {
                         "serviceID"     : "servID",
                         "familyID"      : "famID",
                         }
    
    SERV2FAMILY_COLS  = [ "servID" , "famID" ]
    
    
        
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
        """ create the formatting for the sql columns """
        result = ""
        
        cpt = 0
        for elem in a_list:
            if cpt == 0:
                result += "%s" % (elem)
            else:
                result += ", %s" % (elem)
            cpt += 1

        return result
    
    def _transform_product_table_data(self, a_elem, a_value):
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

    def clean_table(self, a_schema, a_table):
        """ clean a given table """
        
        self._conn.execute("delete from %s.%s;" %(a_schema, a_table))
        
    def get_distribution_type_info(self):
        """ return the distribution info """
        
        result = self._conn.execute("select * from distribution_type")
        
        res_dict = {}
        rows = result.fetch_all()
        
        for row in rows:
            res_dict[row['disID']] = row['name']
        
        return res_dict
        
    
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
        
        #INSERT products_2_distribution (roddID,disID) SELECT p.roddID, p2d.disID FROM products p, products_2_distribution p2d ,distribution_type d WHERE d.name = 'ARCHIVE' and p.internalID = 'EO:EUM:SW:MULT:035'
        insert_in_prod2dis_p1 = "INSERT RODD.products_2_distribution (roddID,disID) SELECT p.roddID, p2d.disID FROM products p, products_2_distribution p2d, distribution_type d WHERE d.name = '%s'"
        
        insert_in_prod2dis_p2 = " and p.internalID = '%s'"

        prod2dis_insert_list = []

        for row in csv_reader:
            cpt_keys    = 0
            values      = ""
            has_changed = False
            
            val = ""
            
            if row.get('EUMETCast') == 'Y':
                val = 'EUMETCAST'
            
            if row.get('GTS') == 'Y':
                val = 'GTS'
            
            if row.get('MSGDirect') == 'Y':
                val = 'MSGDIRECT'
            
            if val == "":
                val = 'ARCHIVE'
            
            prod2dis_insert_list.append(insert_in_prod2dis_p1 % (val))
            internalID = ''
            for elem in a_columns:
                
                #get list of matching keys
                key = lookup_dict.get_key(elem)
                
                if not key:
                    raise Exception("Error: %s as no matching keys in %s" %(elem, LCSVRoddExtractor.PRODUCT_MAPPER))
                
                val = row.get(key[0], None)
                
                # memorize the internalID if necessary
                if elem == "internalID":
                    internalID = val
                
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
                
            insert = insert_line % ("RODD", "products", columns, values)
            
            #print('[r%d]:insert = %s\n' %(nb_rows, insert) )
            #file.write("%s;\n" %(insert))
            self._conn.execute("%s;" %(insert))
            
            for req in prod2dis_insert_list:
                s = req + insert_in_prod2dis_p2 % (internalID)
                self._conn.execute(s)
            
            nb_rows += 1
        
    def read_csv_and_insert_channel_sql(self, a_columns):
        """ 
           read csv channel table 
           
           :param a_columns: list of colums to import
           :type  a_columns: str
        
           :returns: None
            
           :except Exception: if the content cannot be imported
        
        """
        
        csv_reader = csv.DictReader(open('%s/tbl_channels.csv' %(self._root_dir)))
        
        nb_rows = 0
        
        lookup_dict = Lookup(LCSVRoddExtractor.CHANNEL_MAPPER)
        
        # for each line of data create an insert line

        insert_line = "INSERT INTO %s.%s (%s) VALUES (%s)"
        
        
        columns = self._create_sql_columns(a_columns)
        
        #file = open("/tmp/insert_products.sql","w+")

        for row in csv_reader:
            cpt_keys    = 0
            values      = ""
            
            for elem in a_columns:
                
                #get list of matching keys
                key = lookup_dict.get_key(elem)
                
                if not key:
                    raise Exception("Error: %s as no matching keys in %s" %(elem, LCSVRoddExtractor.PRODUCT_MAPPER))
                
                val = row.get(key[0], None)
                
                # and elem == "resources_1"
                if nb_rows == 200 and ("%" in val):
                    print("This is the break")
                
            
                val = "%s" % ( "'%s'" % (val) if val else "NULL")
                    
                # add in values
                if cpt_keys == 0:
                    values += "%s" % ( val )
                else:
                    values += ", %s" % ( val )
                
    
                cpt_keys += 1
                
            insert = insert_line % ("RODD", "channels", columns, values)
            
            #print('[r%d]:insert = %s\n' %(nb_rows, insert) )
            #file.write("%s;\n" %(insert))
            self._conn.execute("%s;" %(insert))
            
            nb_rows += 1
    
    def read_csv_and_insert_families_sql(self, a_columns):
        """ 
           read csv families table 
           
           :param a_columns: list of colums to import
           :type  a_columns: str
        
           :returns: None
            
           :except Exception: if the content cannot be imported
        
        """
        
        csv_reader = csv.DictReader(open('%s/tbl_families.csv' %(self._root_dir)))
        
        nb_rows = 0
        
        lookup_dict = Lookup(LCSVRoddExtractor.FAMILIES_MAPPER)
        
        # for each line of data create an insert line

        insert_line = "INSERT INTO %s.%s (%s) VALUES (%s)"
        
        
        columns = self._create_sql_columns(a_columns)
        
        #file = open("/tmp/insert_products.sql","w+")

        for row in csv_reader:
            cpt_keys    = 0
            values      = ""
            
            for elem in a_columns:
                
                #get list of matching keys
                key = lookup_dict.get_key(elem)
                
                if not key:
                    raise Exception("Error: %s as no matching keys in %s" %(elem, LCSVRoddExtractor.FAMILIES_MAPPER))
                
                val = row.get(key[0], None)
                
                # and elem == "resources_1"
                if nb_rows == 200 and ("%" in val):
                    print("This is the break")
                
            
                val = "%s" % ( "'%s'" % (val) if val else "NULL")
                    
                # add in values
                if cpt_keys == 0:
                    values += "%s" % ( val )
                else:
                    values += ", %s" % ( val )
                
    
                cpt_keys += 1
                
            insert = insert_line % ("RODD", "families", columns, values)
            
            #print('[r%d]:insert = %s\n' %(nb_rows, insert) )
            #file.write("%s;\n" %(insert))
            self._conn.execute("%s;" %(insert))
            
            nb_rows += 1
    
    
    
    def read_csv_and_insert_servicedir_sql(self, a_columns):
        """ 
           read csv channel table 
           
           :param a_columns: list of colums to import
           :type  a_columns: str
        
           :returns: None
            
           :except Exception: if the content cannot be imported
        
        """
        
        csv_services  = csv.DictReader(open('%s/tbl_service.csv' %(self._root_dir)))
        
        # need also the channels
        csv_channels = csv.DictReader(open('%s/tbl_channels.csv' %(self._root_dir)))
        #create ID to channel index
        channels_idx = {}
        for row in csv_channels:
            channels_idx[row['ID']] = row
        
        nb_rows = 0
        
        lookup_dict = Lookup(LCSVRoddExtractor.SERVICE_MAPPER)
        
        # for each line of data create an insert line

        insert_line = "INSERT INTO %s.%s (%s) VALUES (%s)"
        
        
        columns = self._create_sql_columns(a_columns)
        
        #file = open("/tmp/insert_products.sql","w+")

        for row in csv_services:
            cpt_keys    = 0
            values      = ""
            
            for elem in a_columns:
                
                #get list of matching keys
                key = lookup_dict.get_key(elem)
                
                if not key:
                    raise Exception("Error: %s as no matching keys in %s" %(elem, LCSVRoddExtractor.SERVICE_MAPPER))
                
                val = row.get(key[0], None)
                
                #if elem is chanID then we need the right channel ID in the DB
                if elem == "chanID":
                    
                    channel_name = channels_idx[val]['channel']
                    result = self._conn.execute("select chanID from channels where name like '%s'" %(channel_name))
                    
                    val = result.scalar()
                    
                    result.close()
                    
                val = "%s" % ( "'%s'" % (val) if val else "NULL")
                    
                # add in values
                if cpt_keys == 0:
                    values += "%s" % ( val )
                else:
                    values += ", %s" % ( val )
                
    
                cpt_keys += 1
                
            insert = insert_line % ("RODD", "service_dirs", columns, values)
            
            #print('[r%d]:insert = %s\n' %(nb_rows, insert) )
            #file.write("%s;\n" %(insert))
            result = self._conn.execute("%s;" %(insert))
            
            nb_rows += 1
    
    def read_csv_and_insert_product2service_sql(self, a_columns):
        """ 
           read csv channel table 
           
           :param a_columns: list of colums to import
           :type  a_columns: str
        
           :returns: None
            
           :except Exception: if the content cannot be imported
        
        """
        
        csv_services  = csv.DictReader(open('%s/tbl_service.csv'  %(self._root_dir)))
        csv_products  = csv.DictReader(open('%s/tbl_products.csv' %(self._root_dir)))
        
        # need also the channels
        csv_products2service = csv.DictReader(open('%s/tbl-product_service_link.csv' %(self._root_dir)))
        
        
        #create ID to channel index
        service_idx = {}
        for row in csv_services:
            service_idx[row['serviceID']] = row
            
        product_idx = {}
        for row in csv_products:
            product_idx[row['RODDID']] = row
        
        nb_rows = 0
        
        lookup_dict = Lookup(LCSVRoddExtractor.PROD2SERV_MAPPER)
        
        # for each line of data create an insert line

        insert_line = "INSERT INTO %s.%s (%s) VALUES (%s)"
        
        
        columns = self._create_sql_columns(a_columns)
        
        #file = open("/tmp/insert_products.sql","w+")

        for row in csv_products2service:
            cpt_keys    = 0
            values      = ""
            
            for elem in a_columns:
                
                #get list of matching keys
                key = lookup_dict.get_key(elem)
                
                if not key:
                    raise Exception("Error: %s as no matching keys in %s" %(elem, LCSVRoddExtractor.PROD2SERV_MAPPER))
                
                val = row.get(key[0], None)
                
                #if elem is roddID then we need the right channel ID in the DB
                if elem == "roddID":
                    
                    prod_uid = product_idx[val]['InternalID']
                    
                    if not prod_uid:
                        print("No internal id for csv RODDID %s\n" % (val) )
                    
                    #print("produid = %s\n" % (prod_uid))
                    
                    result = self._conn.execute("select roddID from products where internalID like '%s'" %(prod_uid))
                    
                    val = result.scalar()
                    
                    result.close()
                elif elem == "serviceID":
                    
                    service_name = service_idx[val]['service_directory']
                    result = self._conn.execute("select servID from services where name like '%s'" %(service_name))
                    
                    val = result.scalar()
                    
                    
                val = "%s" % ( "'%s'" % (val) if val else "NULL")
                    
                # add in values
                if cpt_keys == 0:
                    values += "%s" % ( val )
                else:
                    values += ", %s" % ( val )
                
    
                cpt_keys += 1
                
            insert = insert_line % ("RODD", "products_2_servdirs", columns, values)
            
            #print('[r%d]:insert = %s\n' %(nb_rows, insert) )
            #file.write("%s;\n" %(insert))
            result = self._conn.execute("%s;" %(insert))
            
            nb_rows += 1
            
    def read_csv_and_insert_service2family_sql(self, a_columns):
        """ 
           read csv channel table 
           
           :param a_columns: list of colums to import
           :type  a_columns: str
        
           :returns: None
            
           :except Exception: if the content cannot be imported
        
        """
        
        csv_services  = csv.DictReader(open('%s/tbl_service.csv'  %(self._root_dir)))
        csv_families  = csv.DictReader(open('%s/tbl_families.csv' %(self._root_dir)))
        
        # need also the channels
        csv_service2family = csv.DictReader(open('%s/tbl_service_family_link.csv' %(self._root_dir)))
        
        
        #create ID to channel index
        service_idx = {}
        for row in csv_services:
            service_idx[row['serviceID']] = row
            
        family_idx = {}
        for row in csv_families:
            family_idx[row['familyID']] = row
        
        lookup_dict = Lookup(LCSVRoddExtractor.SERV2FAMILY_MAPPER)
        
        # for each line of data create an insert line

        insert_line = "INSERT INTO %s.%s (%s) VALUES (%s)"
        
        
        columns = self._create_sql_columns(a_columns)
        
        #file = open("/tmp/insert_products.sql","w+")

        for row in csv_service2family:
            cpt_keys    = 0
            values      = ""
            
            for elem in a_columns:
                
                #get list of matching keys
                key = lookup_dict.get_key(elem)
                
                if not key:
                    raise Exception("Error: %s as no matching keys in %s" %(elem, LCSVRoddExtractor.SERV2FAMILY_MAPPER))
                
                val = row.get(key[0], None)
                
                #if elem is roddID then we need the right channel ID in the DB
                if elem == "familyID":
                    
                    family_name = family_idx[val]['family']
                    
                    if not family_name:
                        print("No internal family name for csv family %s\n" % (val) )
                    
                    #print("produid = %s\n" % (prod_uid))
                    
                    result = self._conn.execute("select famID from families where name like '%s'" %(family_name))
                    
                    val = result.scalar()
                    
                    result.close()
                elif elem == "serviceID":
                    
                    service_name = service_idx[val]['service_directory']
                    result = self._conn.execute("select servID from services where name like '%s'" %(service_name))
                    
                    val = result.scalar()
                    
                    
                val = "%s" % ( "'%s'" % (val) if val else "NULL")
                    
                # add in values
                if cpt_keys == 0:
                    values += "%s" % ( val )
                else:
                    values += ", %s" % ( val )
                
    
                cpt_keys += 1
                
            insert = insert_line % ("RODD", "servdirs_2_families", columns, values)
            
            #print('[r%d]:insert = %s\n' %(nb_rows, insert) )
            #file.write("%s;\n" %(insert))
            result = self._conn.execute("%s;" %(insert))