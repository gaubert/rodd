'''
Created on Nov 8, 2011

@author: guillaume.aubert@eumetcast.int
'''
import sys
import unittest
import base64

import ssl
import gsync


def obfuscate_string(a_str):
    """ use base64 to obfuscate a string """
    return base64.b64encode(a_str)

def deobfuscate_string(a_str):
    """ deobfuscate a string """
    return base64.b64decode(a_str)

def read_password_file(a_path):
    """
       Read log:pass from a file in my home
    """
    f = open(a_path)
    line = f.readline()
    (login, passwd) = line.split(":")
    
    return (deobfuscate_string(login.strip()), deobfuscate_string(passwd.strip()))



class TestGSync(unittest.TestCase):

    def __init__(self, stuff):
        """ constructor """
        super(TestGSync, self).__init__(stuff)
        
        self.login  = None
        self.passwd = None
    
    def setUp(self):
        self.login, self.passwd = read_password_file('/homespace/gaubert/.ssh/passwd')
    
    def ztest_gsync_connect_error(self):
        """
           Test connect error (connect to a wrong port). Too long to check
        """
        has_ssl = True
        gimap = gsync.GIMAPFetcher('imap.gmafil.com', 80, "badlogin", "badpassword", has_ssl)
        
        try:
            gimap.connect()
        except ssl.SSLError, err:
            self.assertEquals(str(err), '[Errno 1] _ssl.c:480: error:140770FC:SSL routines:SSL23_GET_SERVER_HELLO:unknown protocol')
    
    def ztest_gsync_get_capabilities(self):
        """
           Test simple retrieval
        """
        has_ssl = True
        gimap = gsync.GIMAPFetcher('imap.gmail.com', 993, self.login, self.passwd, has_ssl)
        
        gimap.connect()
        
        self.assertEquals(('IMAP4REV1', 'UNSELECT', 'IDLE', 'NAMESPACE', 'QUOTA', 'ID', 'XLIST', 'CHILDREN', 'X-GM-EXT-1', 'XYZZY', 'SASL-IR', 'AUTH=XOAUTH') , gimap.get_capabilities())
    
    def ztest_gsync_check_gmailness(self):
        """
           Test simple retrieval
        """
        has_ssl = True
        gimap = gsync.GIMAPFetcher('imap.gmail.com', 993, self.login, self.passwd, has_ssl)
        
        gimap.connect()
        
        self.assertEquals( True , gimap.check_gmailness())
        
    def ztest_gsync_simple_search(self):
        """
           search all emails before 01.01.2005
        """
        has_ssl = True
        gimap = gsync.GIMAPFetcher('imap.gmail.com', 993, self.login, self.passwd, has_ssl)
        
        gimap.connect()
       
        criteria = ['Before 1-Jan-2011']
        ids = gimap.search(criteria)
        
        self.assertEquals(len(ids), 33629)
        
    def ztest_gsync_retrieve_gmail_ids(self):
        """
           Get all uid before Sep 2004
           Retrieve all GMAIL IDs 
        """
        has_ssl = True
        gimap = gsync.GIMAPFetcher('imap.gmail.com', 993, self.login, self.passwd, has_ssl)
        
        gimap.connect()
       
        criteria = ['Before 1-Oct-2004']
        #criteria = ['ALL']
        ids = gimap.search(criteria)
        
        res = gimap.fetch(ids, [gimap.GMAIL_ID])
        
        self.assertEquals(res, {27362: {'X-GM-MSGID': 1147537963432096749L, 'SEQ': 14535}, 27363: {'X-GM-MSGID': 1147537994018957026L, 'SEQ': 14536}})
        
    def test_gsync_retrieve_all_params(self):
        """
           Get all uid before Sep 2004
           Retrieve all parts for one email
        """
        has_ssl = True
        gimap = gsync.GIMAPFetcher('imap.gmail.com', 993, self.login, self.passwd, has_ssl)
        
        gimap.connect()
       
        criteria = ['Before 1-Oct-2004']
        #criteria = ['ALL']
        ids = gimap.search(criteria)
        
        self.assertEquals(len(ids), 2)
        
        res = gimap.fetch(ids[0], [gimap.GMAIL_ID, gimap.EMAIL_BODY, gimap.GMAIL_THREAD_ID, gimap.GMAIL_LABELS])
        
        self.assertEquals(res[ids[0]][gimap.GMAIL_ID], 1147537963432096749L)
        
        self.assertEquals(res[ids[0]][gimap.EMAIL_BODY],'Message-ID: <6999505.1094377483218.JavaMail.wwwadm@chewbacca.ecmwf.int>\r\nDate: Sun, 5 Sep 2004 09:44:43 +0000 (GMT)\r\nFrom: Guillaume.Aubert@ecmwf.int\r\nReply-To: Guillaume.Aubert@ecmwf.int\r\nTo: aubert_guillaume@yahoo.fr\r\nSubject: Fwd: [Flickr] Guillaume Aubert wants you to see their photos\r\nMime-Version: 1.0\r\nContent-Type: text/plain; charset=us-ascii\r\nContent-Transfer-Encoding: 7bit\r\nX-Mailer: jwma\r\nStatus: RO\r\nX-Status: \r\nX-Keywords:                 \r\nX-UID: 1\r\n\r\n\r\n')
        

def tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGSync)
    unittest.TextTestRunner(verbosity=2).run(suite)
 
if __name__ == '__main__':
    
    tests()