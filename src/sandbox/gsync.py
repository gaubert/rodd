'''
Created on Nov 16, 2011

@author: guillaume.aubert@gmail.com
'''
from imapclient import IMAPClient

class GIMAPer(object):
    '''
    IMAP Class reading the information
    '''


    def __init__(self, host, port, login, password, ssl, use_uid, ):
        '''
            Constructor
        '''
        self.host     = host
        self.port     = port
        self.login    = login
        self.password = password
        self.ssl      = ssl
        self.use_uid  = use_uid
        
        self.server   = None
    
    def connect(self):
        """
           connect to the IMAP server
        """
        self.server = IMAPClient(self.host, port = self.port, use_uid= self.use_uid, ssl= self.ssl)
        
        self.server.login(self.login, self.password)
        
    