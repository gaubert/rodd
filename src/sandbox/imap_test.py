'''
Created on Nov 15, 2011

@author: guillaume.aubert@eumetsat.int
'''
import base64
from imapclient import IMAPClient
import imaplib
    
HOST = 'imap.gmail.com'
PORT = 993
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
    
    return (deobfuscate_string(login.strip()), deobfuscate_string(passwd.strip()))



def imaplib_test(login, password):
    """
       IMAP client
       issue: it is easy to download all emails (as they are in All Mail) and push them back in All Mail.
       However the labels will not be revived as google manages them as imap directories. 
       This could be the easy solution quickly built. 
       A second solution would be for each email to look for the different dirs where they are.
       Maybe IMAP provides a unique id for the emails (too be seen).
    """
    
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(login, password)
    mail.list()
    # Out: list of "folders" aka labels in gmail.
    mail.select("[Gmail]/All Mail") # connect to inbox.
    
    result, data = mail.search(None, "ALL")
    
    ids = data[0] # data is a list.
    
    print("ids = %s\n" %(ids))
    
    id_list = ids.split() # ids is a space separated string
    latest_email_id = id_list[-1] # get the latest

    result, data = mail.fetch(latest_email_id, "(RFC822)") # fetch the email body (RFC822) for the given ID

    raw_email = data[0][1] # here's the body, which is raw text of the whole email
    # including headers and alternate payloads
    print("hello\n")
     

def imapclient__test(login, password):
    
    server = IMAPClient(HOST, use_uid=True, ssl=ssl)
    server.login(login, password)
    
    capabilities = server.capabilities()
    
    print("list folders = %s\n" %(server.list_folders()))
       
    select_info = server.select_folder('[Gmail]/All Mail')
    
    #print '%d messages in INBOX' % select_info['EXISTS']
      
    messages = server.search(['NOT DELETED'])
    print "%d messages in [Gmail]/All Mail" % len(messages)
       
    select_info = server.select_folder('[Gmail]/Sent Mail')
    
    #print '%d messages in INBOX' % select_info['EXISTS']
      
    messages = server.search(['NOT DELETED'])
    print "%d messages in [Gmail]/Sent Mail" % len(messages)   
    
    #response = server.fetch(messages, ['FLAGS', 'RFC822.SIZE', 'RFC822'])
    #for msgid, data in response.iteritems():
    #    print '   ID %d: %d bytes, flags=%s, data=%s' % (msgid, data['RFC822.SIZE'], data['FLAGS'], data['RFC822'])

if __name__ == '__main__':
    
    log, pas = read_password_file('/homespace/gaubert/.ssh/passwd')
    
    imaplib_test(log,pas)
    #imap_test(log, pas)
    