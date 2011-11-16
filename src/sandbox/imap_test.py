'''
Created on Nov 15, 2011

@author: guillaume.aubert@eumetsat.int
'''
import base64
from imapclient import IMAPClient
    
HOST = 'imap.gmail.com'
PORT = 993
USERNAME = ''
PASSWORD = ''
ssl = True

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
    
    return (login.strip(), passwd.strip())



def imap_test():
   
    server = IMAPClient(HOST, use_uid=True, ssl=ssl)
    server.login(USERNAME, PASSWORD)
    
    capabilities = server.capabilities()
    
    print("list folders = %s\n" %(server.list_folders()))
       
    select_info = server.select_folder('INBOX')
    
    print '%d messages in INBOX' % select_info['EXISTS']
      
    messages = server.search(['NOT DELETED'])
    print "%d messages that aren't deleted" % len(messages)
       
    print
    print "Messages:"
    response = server.fetch(messages, ['FLAGS', 'RFC822.SIZE', 'RFC822'])
    for msgid, data in response.iteritems():
        print '   ID %d: %d bytes, flags=%s, data=%s' % (msgid, data['RFC822.SIZE'], data['FLAGS'], data['RFC822'])

if __name__ == '__main__':
    
    log, pas = read_password_file('/homespace/gaubert/.ssh/passwd')
    
    print("obfuscated pass: %s\n" % (deobfuscate_string(pas)))
    print("obfuscated log: %s\n" % (deobfuscate_string(log)))
    
    print(read_password_file('/homespace/gaubert/.ssh/passwd'))
    