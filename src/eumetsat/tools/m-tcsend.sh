#!/bin/bash
set -x
PROC="tc-send"
TARGETDIR="/home/eumetsat"
LOGDIR="/home/eumetsat/data/logs"
IFACE="eth1"
WEBSHELL="http://admin:usingen@10.10.10.165:3516"


# for creating and collecting files when the bug occurs
function createcore () {
cd $TARGETDIR

NOW=`date +"%m-%d-%Y-%T"`
echo -e "$NOW-Starting the tc-send recovery process" >> $TARGETDIR/tc-send-recovery.log

mkdir $COREDIR
cd $COREDIR

tcpdump -ni$IFACE multicast -w cast-server.cap &

echo -e "Old output value:\t\t$old_output_bytes\tbytes" >> monitor.log
echo -e "New output value:\t\t$curr_output_bytes\tbytes" >> monitor.log
echo -e "Calculated output speed for the last 5 minutes:\t\t$output_speed\tbit/s" >> monitor.log

wget $WEBSHELL/www/tsl/sender/scheduled_jobs.html -a monitor.log
wget $WEBSHELL/www/tsl/sender/tsl_sender_statistics.html -a monitor.log
wget $WEBSHELL/www/tsl/sender/trsch_index.html -a monitor.log
wget $WEBSHELL/www/mtpso/bwm_index.html -a monitor.log
wget $WEBSHELL/www/sessions/summary.html -a monitor.log

cp $LOGDIR/send.log $LOGDIR/send.log.1 .
cp $LOGDIR/debug.log* .

top -b -n 1 > top.txt

sleep 5
killall tcpdump

killall -ABRT $PROC
sleep 2
mv $WORKDIR/core* $TARGETDIR/$COREDIR/
tar -czvf $TARGETDIR/$COREDIR.tgz *
rm -rf $TARGETDIR/$COREDIR

NOW=`date +"%m-%d-%Y-%T"`
echo -e "$NOW-End of the tc-send recovery process" >> $TARGETDIR/tc-send-recovery.log

cd

set -m
/etc/init.d/tc-send restart
set +m

}


# create debug logging file
function create_dbg () {
	cat > $WORKDIR/cast-server.dbg <<-EOF
		[debug]
		type=file
		filename=$LOGDIR/debug.log
		file_size=10000000
		file_number=5
		layout="%l:%d{DATETIME}:%-30.30R{%F:%L}:%-30.30f:%m"
		header="Lvl:Date       Time        :Location                      :Function                      :Message"

		[filter]
		level=verbose
		expression="location.tsl.libtsl.shs_role"
		expression="location.tsl.libtsl.trsch_scheduler"
	EOF
}


# infinite main loop
while [ 1 ] ; do
	old_output_bytes=0
	i=0
	# check if TelliCast is running
	pgrep -f $PROC 1>/dev/null 2>&1
	RETVAL=$?
	if [ $RETVAL -eq 0 ] ; then
		while [ 2 ] ;  do
			# get current PID of TelliCast and its working directory
			PID=`pgrep -d " " -f /opt/tellitec/$PROC/$PROC | awk -v FS=" " '{print $1}'`
			WORKDIR=`readlink /proc/$PID/cwd`
			create_dbg
			((i++))

			./monitor_announcement_channel.py 2>>ann_mon_err.log 1>>ann_mon_inf.log
			ret=$?

			if [ ret -gt 0 ] ; then
				COREDIR=vorfall-`date +%Y-%m-%d-%H-%M-%S`
				#createcore
				# core created sleep for 2 minutes 
				sleep 180
				break
			fi
			sleep 10
		done
	else
		# wait in case TelliCast is not running
		sleep 60
	fi
done

exit 0
