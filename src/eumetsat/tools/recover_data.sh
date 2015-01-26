#!/bin/bash



DATE="2015-01-24"
PREV_DATE="2015-01-23"
DEST_DIR=/drives/c/GuillaumeAubertSpecifics/Data/

cd /home/mobaxterm/Dev/ecli-workspace/rodd/src/eumetsat/tools

#recover data for WCM

#Get MET10 data

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET10 -p 'H-000-MSG3*IR_108*-20150124[0-1][0-9][0-5][0-9]-*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET10 -p 'H-000-MSG3__-MSG3________-_________-PRO______-20150124*_,H-000-MSG3__-MSG3________-_________-EPI______-20150124*_'

#Get MET7 data (Done)

#because 201501120000 is in 2015-01-11
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*___-20150123*-*'

#because 201501130000 is in 2015-01-12
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*___-20150124*-*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_2/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MET7 -p 'L-000-MTP___-MET7*PRO______-2015012[3|4]*'

#Get GOES 13 data
#L-000-MSG3__-GOES13______-03_9_075W-PRO______-201501110400-__

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-13 -p 'L-000-MSG3__-GOES13*-20150124*'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-13 -p 'L-000-MSG3__-GOES13______-*-PRO*-20150124[0-9]*-__'

#Get GOES 15 data

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$PREV_DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-15 -p 'L-000-MSG3__-GOES15*-20150124'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/DATE -d $DEST_DIR/$DATE-WCM-Recovered/GOES-15 -p 'L-000-MSG3__-GOES15*-20150124'

#Get MTSAT2
#L-000-MSG3__-MTSAT2______-06_8_145E-PRO______-201501111300-__

python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MTSAT -p 'L-000-MSG3__-MTSAT2*-20150124*-C_'
python file_catcher.py -s /drives/y/archive/EUMETSAT_Data_Channel_3/$DATE -d $DEST_DIR/$DATE-WCM-Recovered/MTSAT -p 'L-000-MSG3__-MTSAT2______-*-PRO*-20150124*-__'


