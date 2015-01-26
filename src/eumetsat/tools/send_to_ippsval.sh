#!/bin/bash

TOP_DIR=/drives/c/GuillaumeAubertSpecifics/Data/2015-01-24-WCM-Recovered
DEST_DIR=/export/home/ipps/cinesat/ape_import/offline/

for file in $TOP_DIR/*/ ; do 
  if [[ -d "$file" && ! -L "$file" ]]; then
    echo "Copy all files from $file on IPPSVal for recovery" 
    scp $file/* ippsval:$DEST_DIR
  fi; 
done
