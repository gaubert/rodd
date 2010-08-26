
import sqlalchemy


from eumetsat.common.utils import ftimer
from eumetsat.common.logging_utils import LoggerFactory


class DatabaseConnector:
    """ Class used to access the IDC database """
    
    def __init__(self,aUrl, a_time_reqs =False):
        
        self._activateTimer = a_time_reqs
        
        self._connected     = False #IGNORE:W0104
        
        self._url = aUrl
        
        self._engine = None
        self._conn   = None
        
        self._log    = LoggerFactory.get_logger(self)
    
    def connect(self):
        """ connect to the database. 
            raise CTBTOError in case of problems
        """
        
        # return if already connected
        if self._connected: 
            return
        
        # preconditions
        if self._url is None: raise Exception("Need a connection url")
 
        self._engine = sqlalchemy.create_engine(self._url)

        self._conn = self._engine.connect()
        
        self._connected = True
        
        self._log.info("Connected to the database %s"%(self._url))
    
    def disconnect(self):
        
        self._conn.close()
        
        self._engine.dispose()
        
        self._connected = False
        
    def isConnected(self):
        return self._connected
       
        
    def getTableMetadata(self,aTableName):
        
        """ Return the metadata related to a table """
        
        self.connect()

        # create MetaData 
        meta = sqlalchemy.MetaData()

        # bind to an engine
        meta.bind = self._engine

        tableMetadata = sqlalchemy.Table(aTableName, meta, autoload=True)

        cols = [] 

        for c in tableMetadata.columns:
            desc = {}
            desc['name']     = c.name
            desc['type']     = c.type
            desc['nullable'] = c.nullable
            cols.append(desc)

        # a dictionary of dict, one dict for each row
        return cols
 
    def execute(self,aSql):
        """execute a sql request on the database"""
        
        sql = sqlalchemy.text(aSql)
        
        if self._activateTimer:
            result = []
            func = self._conn.execute
            t= ftimer(func,[sql],{},result,number=1)
            self._log.debug("\nTime: %s secs \nDatabase: %s\nRequest: %s\n"%(t,self._url,aSql))
            return result[0]
        else:
            result = self._conn.execute(sql)
            return result
        
        
        

    def executeOnEachRow(self,aSql,aTreatment):
        """ run the sql request and execute a treatment on each retrieved row """
       
        sql = sqlalchemy.text(aSql)
        
        result = self._conn.execute(sql)
        
        row = result.fetchone()
        
        while row:
            aTreatment.executeOnRow(row)
            row = result.fetchone()
            
        result.close()
        