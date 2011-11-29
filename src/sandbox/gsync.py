'''
Created on Nov 16, 2011

@author: guillaume.aubert@gmail.com
'''
from imapclient import IMAPClient

class GIMAPFetcher(object):
    '''
    IMAP Class reading the information
    '''
    GMAIL_EXTENSION   = 'X-GM-EXT-1'  # GMAIL capability
    GMAIL_ALL         = '[Gmail]/All Mail' #GMAIL All Mail mailbox
    GMAIL_ID          = 'X-GM-MSGID' #GMAIL ID attribute
    GMAIL_THREAD_ID   = 'X-GM-THRID'
    GMAIL_LABELS      = 'X-GM-LABELS'
    
    EMAIL_BODY        = 'RFC822'


    def __init__(self, host, port, login, password, ssl, use_uid = True):
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
        
        # set to GMAIL_ALL dir by default and in readonly
        self.server.select_folder(GIMAPFetcher.GMAIL_ALL, readonly = True)
        
        
    def get_capabilities(self):
        """
           return the server capabilities
        """
        if not self.server:
            raise Exception("GIMAPFetcher not connect to the GMAIL server")
        
        return self.server.capabilities()
    
    def check_gmailness(self):
        """
           Check that the server is a gmail server
        """
        if not GIMAPFetcher.GMAIL_EXTENSION in self.get_capabilities():
            raise Exception("GIMAPFetcher is not connect to a IMAP GMAIL server. Please check host (%s) and port (%s)" % (self.host, self.port))
        
        return True
    
    def search(self, a_criteria):
        """
           Return all found ids corresponding to the search
        """
        return self.server.search(a_criteria)
    
    def fetch(self, a_ids, a_attributes):
        """
           Return all attributes associated to each message
        """
        return self.server.fetch(a_ids, a_attributes)
    
    