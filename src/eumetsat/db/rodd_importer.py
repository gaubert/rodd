'''
Created on 25 Jun 2010

@author: guillaume.aubert@eumetsat.int
'''
import sqlalchemy

class RoddImporter(object):
    
    """ Generic Importer
    """
    
    def __init__(self, a_db_url):
        
        self._db_url = a_db_url
        
        self._ops_engine  = sqlalchemy.create_engine(self._db_url)
        self._ops_conn    = self._ops_engine.connect()
    
    def done(self):
        print("This is done\n")