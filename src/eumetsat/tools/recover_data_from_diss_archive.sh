#!/bin/bash
#set -x

#Dest Dir Change if you wish to get the data copied somewhere else
DEST_DIR=/drives/c/GuillaumeAubertSpecifics/Data/
#Dir from where the script has to be run
SCRIPT_DIR=/home/mobaxterm/Dev/ecli-workspace/rodd/src/eumetsat/tools

#MANAGE arguments and compute the dates for the previous day
if [ "$#" -ne 1 ]; then
    echo "Error: Illegal number of parameters. $0 requires a date yyyy-mm-dd, .e.g 2015-02-01."
    echo "Passed arguments: [$@]"
    exit 1;
fi

DATE="$1"

#go to dir of script for the moment
cd $SCRIPT_DIR

#compute date -1 day with python utility
IN=`./minus_x_days.py $DATE`
result="$?"

if [ $result -ne 0 ]; then
  echo "$IN"
  exit 0
fi

#Parse the results provided by minus_x_days.py => return yyyymmdd, yyyy-mm-(dd-1), yyyymm(dd-1)
arr=(${IN//,/ })
EUMDATE=${arr[0]}
FDATE=${arr[1]}
PREV_DATE=${arr[2]}
FPREV_DATE=${arr[3]}

#echo $DATE
#echo $EUMDATE
#echo $FDATE
#echo $PREV_DATE
#echo $FPREV_DATE

echo "Recovering WCM data for $DATE in $DEST_DIR/$DATE-WCM-Recovered."

#recover data for WCM
#Get MET10 data

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/MET10 -p 'H-000-MSG3*IR_108*-'"$FDATE"'*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/MET10 -p 'H-000-MSG3__-MSG3________-_________-PRO______-'"$FDATE"'*_,H-000-MSG3__-MSG3________-_________-EPI______-'"$FDATE"'*_'

#Get MET7 data (Done)

#because 201501120000 is in 2015-01-11
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*___-'"$FDATE"'*-*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*PRO______-'"$FDATE"'*'

#because 201501130000 is in 2015-01-12
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*___-'"$FDATE"'*-*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*PRO______-'"$FDATE"'*'

#Get GOES 13 data
#L-000-MSG3__-GOES13______-03_9_075W-PRO______-201501110400-__

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-13 -p 'L-000-MSG3__-GOES13*-'"$FDATE"'*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-13 -p 'L-000-MSG3__-GOES13______-*-PRO*-'"$FDATE"'*-__'

#Get GOES 15 data

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-15 -p 'L-000-MSG3__-GOES15*'"$FDATE"'*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-15 -p 'L-000-MSG3__-GOES15*'"$FDATE"'*'

# GET HIMAWARI
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_4/$EUMDATE -d $DEST_DIR/$DATE-WCM-Recovered/HIMAW -p 'IMG_DK01IR1*_'"$FDATE"'*.bz2'
