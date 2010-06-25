# Echo server program
import socket

HOST = ''                 # Symbolic name meaning the local host
PORT = 9001               # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print "listenning on %s , port = %d"%(HOST,PORT)
while 1:
    conn, addr = s.accept()
    print 'Connected by', addr
    while 1:
        try:
            data = conn.recv(1024)
            print "received = ", data
            if data[:4] == "QUIT":
               conn.send("BYE BYE")
               conn.close()
            if not data: break
            conn.send(data)
        except :
            print "exception received"
            break
    conn.close()
