import MySQLdb

# connection on windows
#conn = MySQLdb.connect (host = "127.0.0.1", user="root", db = "RODD")
conn = MySQLdb.connect (host = "tclxs30", user="rodd",  passwd="ddor", db = "RODD")
cursor = conn.cursor ()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
print "server version:", row[0]
cursor.close ()

cursor = conn.cursor ()
cursor.execute ("SELECT * from format_type")
rows = cursor.fetchall ()

for row in rows:
    print "server version:", row

cursor.close ()

conn.close ()
