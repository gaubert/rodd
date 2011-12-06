'''
Created on Nov 16, 2011

@author: guillaume.aubert@gmail.com
'''
import json
import gzip
import re
import time
from imapclient import IMAPClient
import gsync_utils as gsync_utils

class GIMAPFetcher(object):
    '''
    IMAP Class reading the information
    '''
    GMAIL_EXTENSION   = 'X-GM-EXT-1'  # GMAIL capability
    GMAIL_ALL         = '[Gmail]/All Mail' #GMAIL All Mail mailbox
    GOOGLE_MAIL_ALL   = '[Google Mail]/All Mail' #Google Mail All Mail mailbox for Germany
    GMAIL_ID          = 'X-GM-MSGID' #GMAIL ID attribute
    GMAIL_THREAD_ID   = 'X-GM-THRID'
    GMAIL_LABELS      = 'X-GM-LABELS'
    
    IMAP_INTERNALDATE = 'INTERNALDATE'
    IMAP_FLAGS        = 'FLAGS'
    IMAP_BODY_PEEK    = 'BODY.PEEK[]'
    
    EMAIL_BODY        = 'RFC822'
    
    GET_ALL_INFO = [ GMAIL_ID, GMAIL_THREAD_ID, GMAIL_LABELS, IMAP_INTERNALDATE, EMAIL_BODY, IMAP_FLAGS, IMAP_BODY_PEEK]

    GET_ALL_BUT_DATA = [ GMAIL_ID, GMAIL_THREAD_ID, GMAIL_LABELS, IMAP_INTERNALDATE, IMAP_FLAGS]
 

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
    
    def connect(self, go_to_all_folder = True, readonly_folder = True):
        """
           connect to the IMAP server
        """
        self.server = IMAPClient(self.host, port = self.port, use_uid= self.use_uid, ssl= self.ssl)
        
        self.server.login(self.login, self.password)
        
        self._all_mail_folder = None
        
        #find the all mail folder
        self.find_all_mail_folder()
        
        # set to GMAIL_ALL dir by default and in readonly
        if go_to_all_folder:
            self.server.select_folder(self._all_mail_folder, readonly = readonly_folder)
    
    def find_all_mail_folder(self):
        """
           depending on your account the all mail folder can be named 
           [GMAIL]/ALL Mail or [GoogleMail]/All Mail.
           Find and set the right one
        """
        
        folders = self.server.list_folders()
        dir = None
        for (_, _, dir) in folders:
            if dir == GIMAPFetcher.GMAIL_ALL:
                self._all_mail_folder = GIMAPFetcher.GMAIL_ALL
                break
            elif dir == GIMAPFetcher.GOOGLE_MAIL_ALL:
                self._all_mail_folder = GIMAPFetcher.GOOGLE_MAIL_ALL
                break
        
        if dir == None:
            #Error
            raise Exception("Cannot find global dir %s or %s. Are you sure it is a GMail account" % (GIMAPFetcher.GMAIL_ALL, GIMAPFetcher.GOOGLE_MAIL_ALL))
            
        
    
    def get_all_folders(self): 
        """
           Return all folders mainly for debuging purposes
        """
        return self.server.list_folders()
        
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
    
    def store_email(self, a_id, a_body, a_flags, a_internal_time, a_labels):
        """
           Push a complete email body 
        """
        #protection against myself
        if self.login == 'guillaume.aubert@gmail.com':
            raise Exception("Cannot push to this account")
        
        res = self.server.append(self._all_mail_folder, a_body, a_flags, a_internal_time)
        
        result_uid = int(re.search('^[APPENDUID [0-9]* ([0-9]*)] \(Success\)$', res).group(1))

        
        # add GMAIL LABELS 
        if len(a_labels) > 0:
            
            labels_str = '('
            for label in a_labels:
                labels_str += '%s ' %(label)
            labels_str = '%s%s' % (labels_str[:-1],')')
            
            #labels_str = '("'+'" "'.join(a_labels)+'")'
            r, d = self.server._imap.uid('STORE', result_uid, '+X-GM-LABELS', labels_str)

        
        
        return res
        
        
    
class GmailStorer(object):
    '''
       Store emails
    ''' 
    ID_FLAG="#ID:"
    THREAD_ID_FLAG="#THRID:"
    LABELS_FLAG="#LABELS:"
    EMAIL_FLAG="#EMAIL:"
    
    def __init__(self, a_storage_dir):
        """
           Store on disks
        """
        self._top_dir = a_storage_dir
        
        gsync_utils.makedirs(a_storage_dir)
        

    def store_email(self, id, email, thread_ids, labels, internal_date, flags, compress = False):
        """
           store a json structure with all email elements in a file
           If compress is True, use gzip compression
        """
        path = "%s/%s.eml" % (self._top_dir, id)
        
        if compress:
            path = '%s.gz' % (path)
            f_desc = gzip.open(path, 'wb')
        else:
            f_desc = open(path, 'w')
        
        #create json structure
        json_obj= { 'id'            : id,
                    'email'         : email,
                    'thread_ids'    : thread_ids,
                    'labels'        : labels,
                    'internal_date' : gsync_utils.datetime2e(internal_date),
                    'flags'         : flags}
        
        json.dump(json_obj, f_desc, ensure_ascii = False)
        
        f_desc.flush()
        
        f_desc.close()
        
        return path
        
    def restore_email(self, file_path, compress = False):
        """
           Restore an email
        """
        if compress:
            f_desc = gzip.open(file_path, 'r')
        else:
            f_desc = open(file_path,'r')
        
        res = json.load(f_desc)
        
        res['internal_date'] =  gsync_utils.e2datetime(res['internal_date'])
        
        return res
        
    
    