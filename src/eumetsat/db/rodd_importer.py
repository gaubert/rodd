'''
Created on 25 Jun 2010

@author: guillaume.aubert@eumetsat.int
'''
import sqlalchemy

class RoddImporter(object):
    """ Generic Importer
    """
    
    TABLE_PRODUCTS = "products"
    
    def __init__(self, a_db_url):
        
        self._db_url = a_db_url
        
        self._engine  = sqlalchemy.create_engine(self._db_url)
        
        self._conn    = self._engine.connect()
        
        # create MetaData 
        self._metadata      = sqlalchemy.MetaData()

        # bind to an engine
        # need to be binded to the engine now as the tables 
        # will use the reflection mechanism to be populated
        self._metadata.bind = self._engine
        
        self._schema      = "rodd"
    
    def done(self):
        print("This is done\n")
        
    
    def import_table_products(self, a_values):
        """
            import into the table product
          
            :param a_values: values to import
            :type  a_values: str
        
            :returns: None
            
            :except Exception: if the content cannot be imported
        """
        
        # get the columns names with a dummy request
        products_table = sqlalchemy.Table(RoddImporter.TABLE_PRODUCTS, self._metadata, schema= self._schema, autoload=True)
        
        print("products table %s\n" %(products_table.columns))
        
        columns_str = ""
        i = 0
        for column in products_table.columns:
            # create columns in insert just once
            if i == 0:
                columns_str += "%s" %(column)
            else:
                columns_str += ", %s" %(column)
        
            i += 1
        
        print("Columns:(%s)\n" %(columns_str))
        
        #results = self._conn.execute("select * from %s.%s limit 1" % (self._schema, RoddImporter.TABLE_PRODUCTS))
        
        #for row in results:
        #    print(row)
        
        