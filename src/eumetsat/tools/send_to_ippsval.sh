#!/bin/bash
#set -x

#Destination dir on ippsval
DEST_DIR=/export/home/ipps/cinesat/ape_import/offline/

#MANAGE arguments and compute the dates for the previous day
if [ "$#" -ne 1 ]; then
    echo "Error: Illegal number of parameters. $0 requires a date yyyy-mm-dd, .e.g 2015-02-01."
    echo "Passed arguments: [$@]"
    exit 1;
fi

DATE="$1"

#Top source dir
TOP_DIR=/drives/c/GuillaumeAubertSpecifics/Data/$DATE-WCM-Recovered


for file in $TOP_DIR/*/ ; do 
  if [[ -d "$file" && ! -L "$file" ]]; then
    echo "Copy all files from $file on IPPSVal for recovery" 
    scp $file/* ippsval:$DEST_DIR
  fi; 
done
