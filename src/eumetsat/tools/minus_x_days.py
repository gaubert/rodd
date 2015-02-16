#!/bin/python
#small script providing the dates for recovering the data of the WCM for a paticular day

import sys
from datetime import datetime, date, timedelta

try:
   if len(sys.argv) != 2:
      print("Error. Need to pass only one argument. Passed command line %s" % (sys.argv))
      sys.exit(1)

   today = date.today()
   given_dt = datetime.strptime(sys.argv[1], "%Y-%m-%d")
   days_to_substract=1

   # if current day is today then return EUMDate = today else EUMDate = given_dt
   eum_dt = ""
   if today == given_dt.date():
      eum_dt = "today"
   else:
      eum_dt = given_dt.strftime("%Y-%m-%d")

   d = given_dt - timedelta(days=days_to_substract)

   #return EUMDate, FDate, PREV_DATE, FPREV_DATE
   print("%s,%s,%s,%s" % (eum_dt, given_dt.strftime("%Y%m%d"),d.strftime("%Y-%m-%d"), d.strftime("%Y%m%d")))
   sys.exit(0)
except Exception, e:
   print("Error: %s." % (e))
   print("Passed date [%s] is not correclty formatted. Supported format yyyy-mm-dd." % (sys.argv[1]))
   sys.exit(1)

