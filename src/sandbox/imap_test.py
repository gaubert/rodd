'''
Created on Nov 15, 2011

@author: guillaume.aubert@eumetsat.int
'''

from imapclient import IMAPClient
    
HOST = 'imap.gmail.com'
PORT = 993
USERNAME = ''
PASSWORD = ''
ssl = True
   
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
    pass