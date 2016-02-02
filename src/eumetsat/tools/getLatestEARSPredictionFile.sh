#!/bin/bash
#set -x

DATE=`date +%y-%m-%d`

#FILE="ears_avhrr_pass_prediction_DATE.txt.xhtml"
FILE="ears_atovs_pass_prediction_DATE.txt.xhtml"

SERV="http://oiswww.eumetsat.org/uns/webapps/ears/"
OUTPUTDIR=/tmp

finished=false
days=0
maxdays=20

while  [ "${finished}" != "true" ]; do

   CURR_FILE=`echo "$FILE" | sed s/DATE/"$DATE"/g`
   URL="$SERV$CURR_FILE"
   echo "Trying to get $URL"
   wget $URL -O "$OUTPUTDIR/$CURR_FILE" -o /tmp/wgetoutputs.log
   size=$(du -k "$OUTPUTDIR/$CURR_FILE" | cut -f 1)
   if [ $size -gt 0 ]; then
      echo "Got the latest pass prediction file from $DATE. It is available in $OUTPUTDIR/$CURR_FILE "
      finished=true
   else
      echo "No prediction files for $DATE. Try for one day earlier."
      rm -f "$OUTPUTDIR/$CURR_FILE"

      ((days+=1))
      if [ $days -ge $maxdays ]; then
         echo "Something went wrong. Try the last $maxdays days and could not get any prediction files. Quit on error."
         exit 1
      fi
      DATE="$(date "+%y-%m-%d" -d "$days days ago")"
   fi
done

exit 0



