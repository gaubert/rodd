import ftplib
import sys
import os

def upload(filename, server, login, passwd, directory):
	try:
			s = ftplib.FTP(server,login,passwd) # Connect

			passive=True
			print("--- Set passive to %s\n" %( passive) )

			s.set_pasv(passive)

			s.cwd(directory)

			f = open(filename,'rb')                # file to send

			basen = os.path.basename(filename)
			print("--- Upload %s\n" %(basen) )
			s.storbinary('STOR %s.tmp' % (basen) , f)         # Send the file

			print("--- Rename %s.tmp in %s\n" %(basen, basen) )

			s.rename('%s.tmp' % (basen) , basen)

			print("--- Everything was fine. Ciao\n")

			f.close()                                # Close file and FTP
			s.quit()
	except Exception, e:
		print("Error:\n")
		print(e)
		sys.exit(1)

if __name__ == '__main__':

    filename=None

    if len(sys.argv) != 2:
       print("Error: need a filename to upload")
       sys.exit(1)
    else:
       filename=sys.argv[1]
       print("--- Filename to upload: %s\n" %( filename) )

    server='xxxxxxxxxxxxx'

    login='xxxxxxxxxx'
    passwd='xxxxxxxxx'
    directory='xxxxxxxxxxx'

    upload(filename,server,login,passwd,directory)

