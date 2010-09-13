'''
Created on Sep 13, 2010

@author: guillaume.aubert@eumetsat.int
'''
import sqlalchemy


from eumetsat.common.utils import ftimer
from eumetsat.common.logging_utils import LoggerFactory


class DatabaseConnector:
    """ Class used to access the IDC database """
    
    def __init__(self, a_url, a_time_reqs =False):
        """ constructor """
        self._activate_timer = a_time_reqs
        
        self._connected     = False #IGNORE:W0104
        
        self._url           = a_url
        
        self._engine        = None
        self._conn          = None
        self._metadata      = None
        
        self._log           = LoggerFactory.get_logger(self)
    
    def connect(self):
        """ connect to the database. 
            raise CTBTOError in case of problems
        """
        
        # return if already connected
        if self._connected: 
            return
        
        # preconditions
        if self._url is None: 
            raise Exception("Need a connection url")
 
        self._engine = sqlalchemy.create_engine(self._url)

        self._conn = self._engine.connect()
        
        self._metadata  = sqlalchemy.MetaData(bind=self._engine)
        
        self._connected = True
        
        self._log.info("Connected to the database %s"%(self._url))
    
    def disconnect(self):
        """ close connection """
        self._conn.close()
        
        self._engine.dispose()
        
        self._connected = False
        
    def is_connected(self):
        """ is connected ? """
        return self._connected
       
        
    def get_table_metadata(self, a_table_name):
        """ Return the metadata related to a table """
        
        self.connect()

        # create MetaData 
        meta = sqlalchemy.MetaData()

        # bind to an engine
        meta.bind = self._engine

        table_metadata = sqlalchemy.Table(a_table_name, meta, autoload = True)

        cols = [] 

        for col in table_metadata.columns:
            desc = {}
            desc['name']     = col.name
            desc['type']     = col.type
            desc['nullable'] = col.nullable
            cols.append(desc)

        # a dictionary of dict, one dict for each row
        return cols
    
    def execute(self, a_sql_obj):
        """ proxy to sqlaclhemy execute """
        
        # if sql_obj is a string wrap it in a sqlalchemy.text
        
        if type(a_sql_obj) == type(''):
            sql = sqlalchemy.text(a_sql_obj)
        else:
            sql = a_sql_obj
        
        if self._activate_timer:
            result = []
            func = self._conn.execute
            the_timer = ftimer(func, [sql], {}, result, number = 1)
            self._log.debug("\nTime: %s secs \nDatabase: %s\nRequest: %s\n"%(the_timer, self._url, sql))
            return result[0]
        else:
            result = self._conn.execute(sql)
            return result
 
    def execute_sql(self, a_sql):
        """execute a sql request on the database"""
        
        sql = sqlalchemy.text(a_sql)
        
        if self._activate_timer:
            result = []
            func = self._conn.execute
            the_timer = ftimer(func, [sql], {}, result, number = 1)
            self._log.debug("\nTime: %s secs \nDatabase: %s\nRequest: %s\n"%(the_timer, self._url, a_sql))
            return result[0]
        else:
            result = self._conn.execute(sql)
            return result
        
        
        

    def execute_on_each_row(self, a_sql, a_treatment):
        """ run the sql request and execute a treatment on each retrieved row """
       
        sql = sqlalchemy.text(a_sql)
        
        result = self._conn.execute(sql)
        
        row = result.fetchone()
        
        while row:
            a_treatment.executeOnRow(row)
            row = result.fetchone()
            
        result.close()
        