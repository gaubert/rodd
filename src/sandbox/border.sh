#!/bin/bash
# assumptions:  
#   windows ids are at least 5 digits long
#   we dont need to bother with windows that have no name
#   "first argument" from the pipe is east (could be west)
#   
#set -x

xprop -id $1 |\
        grep -Ee '^(_NET_FRAME_EXTENTS|WM_CLASS)' |\
        sed 's/.*=\ //' |\
        sed -e :a -e '/$/N;s/\n/ /;ta' |\
        grep  ^[0-9]    |\
while read line;
 do
        set -- $line
        E=`echo $1|sed 's/,$//'`
        W=`echo $2|sed 's/,$//'`
        N=`echo $3|sed 's/,$//'`
        S=`echo $4|sed 's/,$//'`
        NAME=`echo $5|sed 's/,$//'`
        CLASS=`echo $6|sed 's/,$//'`
        echo -e "$CLASS $NAME N=$N, E=$E S=$S W=$W"
 done
