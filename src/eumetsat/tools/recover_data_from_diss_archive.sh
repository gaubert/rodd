#!/bin/bash
set -x


DATE="2015-02-13"
FDATE="20150213"
PREV_DATE="2015-02-12"
FPREV_DATE="20150212"
DEST_DIR=/drives/c/GuillaumeAubertSpecifics/Data/

cd /home/mobaxterm/Dev/ecli-workspace/rodd/src/eumetsat/tools

#recover data for WCM

#Get MET10 data

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET10 -p 'H-000-MSG3*IR_108*-'"$FDATE"'*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET10 -p 'H-000-MSG3__-MSG3________-_________-PRO______-'"$FDATE"'*_,H-000-MSG3__-MSG3________-_________-EPI______-'"$FDATE"'*_'

#Get MET7 data (Done)

#because 201501120000 is in 2015-01-11
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*___-'"$FDATE"'*-*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*PRO______-'"$FDATE"'*'

#because 201501130000 is in 2015-01-12
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*___-'"$FDATE"'*-*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*PRO______-'"$FDATE"'*'

#Get GOES 13 data
#L-000-MSG3__-GOES13______-03_9_075W-PRO______-201501110400-__

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-13 -p 'L-000-MSG3__-GOES13*-'"$FDATE"'*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-13 -p 'L-000-MSG3__-GOES13______-*-PRO*-'"$FDATE"'*-__'

#Get GOES 15 data

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-15 -p 'L-000-MSG3__-GOES15*'"$FDATE"'*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-15 -p 'L-000-MSG3__-GOES15*'"$FDATE"'*'

#Get MTSAT2
#L-000-MSG3__-MTSAT2______-06_8_145E-PRO______-201501111300-__

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MTSAT -p 'L-000-MSG3__-MTSAT2*-'"$FDATE"'*-C_'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MTSAT -p 'L-000-MSG3__-MTSAT2______-*-PRO*-'"$FDATE"'*-__'


