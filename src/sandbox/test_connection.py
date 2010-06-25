import MySQLdb

#conn = MySQLdb.connect (host = "localhost", user = "testuser", passwd = "testpass", db = "test")
conn = MySQLdb.connect (host = "127.0.0.1", user="root", db = "rodd")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
print "server version:", row[0]
cursor.close ()
conn.close ()
