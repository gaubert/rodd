'''
Created on Nov 16, 2011

@author: guillaume.aubert@gmail.com
'''
import json
import gzip
import re
import datetime
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
    IMAP_ALL          = 'ALL'
    
    EMAIL_BODY        = 'BODY[]'
    
    #to be removed
    EMAIL_BODY_OLD        = 'RFC822' #set msg as seen
    IMAP_BODY_PEEK    = 'BODY.PEEK[]' #get body without setting msg as seen
    
    
    #GET_IM_UID_RE
    APPENDUID = '^[APPENDUID [0-9]* ([0-9]*)] \(Success\)$'
    
    APPENDUID_RE = re.compile(APPENDUID)
    
    GET_ALL_INFO = [ GMAIL_ID, GMAIL_THREAD_ID, GMAIL_LABELS, IMAP_INTERNALDATE, IMAP_BODY_PEEK, IMAP_FLAGS]

    GET_ALL_BUT_DATA = [ GMAIL_ID, GMAIL_THREAD_ID, GMAIL_LABELS, IMAP_INTERNALDATE, IMAP_FLAGS]
 

    def __init__(self, host, port, login, password, readonly_folder = True):
        '''
            Constructor
        '''
        self.host            = host
        self.port            = port
        self.login           = login
        self.password        = password
        self.ssl             = True
        self.use_uid         = True
        self.readonly_folder = readonly_folder
        
        self.server          = None
    
    def connect(self, go_to_all_folder = True):
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
            self.server.select_folder(self._all_mail_folder, readonly = self.readonly_folder)
    
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
    
    def _build_labels_str(self, a_labels):
        """
           Create IMAP label string from list of given labels
           a_labels: List of labels
        """
        # add GMAIL LABELS 
        labels_str = None
        if a_labels and len(a_labels) > 0:
            labels_str = '('
            for label in a_labels:
                labels_str += '%s ' %(label)
            labels_str = '%s%s' % (labels_str[:-1],')')
        
        return labels_str
        
    
    def store_email(self, a_id, a_body, a_flags, a_internal_time, a_labels):
        """
           Push a complete email body 
        """
        #protection against myself
        if self.login == 'guillaume.aubert@gmail.com':
            raise Exception("Cannot push to this account")
        
        res = self.server.append(self._all_mail_folder, a_body, a_flags, a_internal_time)
        
        # check res otherwise Exception
        if '(Success)' not in res:
            raise Exception("GIMAPFetcher cannot restore email in %s account." %(self.login))
        
        result_uid = int(GIMAPFetcher.APPENDUID_RE.search(res).group(1))
        
        labels_str = self._build_labels_str(a_labels)
        
        if labels_str:  
            #has labels so update email  
            ret_code, data = self.server._imap.uid('STORE', result_uid, '+X-GM-LABELS', labels_str)
        
            # check if it is ok otherwise exception
            if ret_code != 'OK':
                raise Exception("Cannot add Labels %s to email with uid %d. Error:%s" % (labels_str, result_uid, data))
        
        return result_uid
            
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
        
class GSyncer(object):
    """
       Main object operating over gmail
    """ 
    
    def __init__(self, db_root_dir, host , port, login , passwd):
        """
           constructor
        """   
        self.db_root_dir = db_root_dir
        
        #create dir if it doesn't exist
        gsync_utils.makedirs(self.db_root_dir)
        
        
        # create source and try to connect
        self.src = GIMAPFetcher(host, port, login, passwd)
        self.src.connect()
        
    def _sync_between(self, begin_date, end_date, storage_dir, compress = True):
        """
           sync between 2 dates
        """
        #for the moment compress = False
        compress = False
        
        #create storer
        gstorer = GmailStorer(storage_dir)
        
        #search before the next month
        imap_req = 'Before %s' % (gsync_utils.datetime2imapdate(end_date))
        
        ids = self.src.search(imap_req)
                              
        #loop over all ids, get email store email
        for id in ids:
            
            #retrieve email from destination email account
            data      = self.src.fetch(id, GIMAPFetcher.GET_ALL_INFO)
            
            file_path = gstorer.store_email(data[id][GIMAPFetcher.GMAIL_ID], \
                               data[id][GIMAPFetcher.EMAIL_BODY], \
                               data[id][GIMAPFetcher.GMAIL_THREAD_ID], \
                               data[id][GIMAPFetcher.GMAIL_LABELS], \
                               data[id][GIMAPFetcher.IMAP_INTERNALDATE], \
                               data[id][GIMAPFetcher.IMAP_FLAGS], \
                               compress = compress)
            
            print("Stored email %d in %s" %(id, file_path))
        
    def _get_next_date(self, a_current_date):
        """
           return the next date necessary to build the imap req
        """
        dummy_date = a_current_date.replace(day=1)
        
        # the next date = current date + 1 month
        return dummy_date + datetime.timedelta(days=31)
    
    def sync(self):
        """
           sync with db on disk
        """
        
        # get all id in All Mail
        ids = self.src.search(GIMAPFetcher.IMAP_ALL)
        
        #ids[0] should be the oldest so get the date and start from here
        res  = self.src.fetch(ids[0], GIMAPFetcher.GET_ALL_BUT_DATA )
        
        current_date = res[ids[0]][GIMAPFetcher.IMAP_INTERNALDATE]
        
        now_date = datetime.datetime.now() + datetime.timedelta(days=1)
        
        #create next date strating to the first day of the current month and adding one month
        next_date    = self._get_next_date(current_date)
        
        while next_date < now_date:
            # create db dir for the retrieved month
            
            db_dir = '%s/%s' %(self.db_root_dir, gsync_utils.get_ym_from_datetime(current_date))
            
            self._sync_between(current_date, next_date, db_dir)
            
            current_date = next_date
            next_date    = self._get_next_date(current_date)
        
        #will have to do up to now_date
            
        
    