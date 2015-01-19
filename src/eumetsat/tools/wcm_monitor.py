#!/usr/bin/python
'''
Created on Jan 14, 2015

@author: guillaume.aubert@eumetsat.int
'''
import os
import time
import smtplib
import datetime
import traceback

DEBUG = False


def previous_quater_dt(dt):
    """
    Get a datetime
    :param dt: datetime from which to get the previous quater
    :return: a datetime which is the previous quater of hour
    """
    # how many secs have passed this hour
    nsecs = dt.minute * 60 + dt.second + dt.microsecond * 1e-6
    delta = nsecs - (nsecs // 900) * 900
    # time + number of seconds to quarter hour mark.
    return dt - datetime.timedelta(seconds=delta)

def get_formatted_ts():
    """
    :return: Formatted Timestamp to go into log messages
    """
    return datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")


class WCMMonitor(object):
    SERVER = "localhost"
    FROM = "wcm_monitor@eumetsat.int"
    TO = ["guillaume.aubert@eumetsat.int"]
    SUBJECT = "Potential errors. Data missing on IPPSVAL"

    #formatting must be kept like that
    MSG_TEMPLATE = """\
From: %s
To: %s
Subject: %s

%s
"""

    MAX_WARNINGS_PER_DAY = 3 #nb of emails sent for one file

    def __init__(self, a_file_pattern, a_src_dir, a_sleep_time):
        """

        :param file_pattern:
        :param src_dir:
        :param sleep_time: sleeping time in seconds
        :return:
        """
        self._file_pattern = a_file_pattern
        self._src_dir      = a_src_dir
        self._sleep_time   = a_sleep_time

        #send 3 emails and stop to advertise the error
        self._warnings_sent  = 0
        self._daily_missings = []

    @classmethod
    def get_list_of_time_since_midnight(cls, the_datetime):
        """
         Return as a datetime the list of 15 min time since midnight.
        :rtype : list of time since midnight
        """
        result = []

        # look at the files from - 15 min to let some time for the generation
        curr_dt = the_datetime - datetime.timedelta(minutes=15)

        first_dt = curr_dt.replace(hour=00, minute=00)

        curr_dt = previous_quater_dt(curr_dt)

        while curr_dt > first_dt:
            curr_dt = previous_quater_dt(curr_dt - datetime.timedelta(minutes=1))
            #print("curr_dt = %s" % curr_dt )
            result.append(curr_dt.strftime('%y%m%d%H%M'))

        return result

    def monit(self):
        """
        Run the monitoring
        :return: None
        """
        curr_datetime = datetime.datetime.now()

        # get dir of the current day
        the_day_dir = curr_datetime.strftime('%Y-%m-%d')

        dates = self.get_list_of_time_since_midnight(curr_datetime)

        the_dir = self._src_dir % (the_day_dir)

        #special case around midnight because the target dir is not created before ~ 00:20.
        #only start the monitoring after 00:30.
        thresold_time = datetime.time(0, 30, 0)

        #send daily report at midnight
        if datetime.time(0,00,00) < curr_datetime.time() < datetime.time(0,15,00):
            self.send_daily_report(the_dir, the_day_dir)
            #reset daily missing
            self._daily_missings = []

        if curr_datetime.time() < thresold_time:
            print("%s-Info: Wait until 00:30 before to monitor in %s" % (get_formatted_ts(), the_dir))
            return

        the_files = sorted(os.listdir(the_dir))

        if DEBUG:
            print("DEBUG: list of files = %s" % (the_files))

        #foreach dates look in the dir if the file is here
        for the_date in sorted(dates):
            filename = file_pattern % (the_date)
            if filename not in the_files and filename not in self._daily_missings: # file not found
                self._daily_missings.append(filename)
                #new file is missing (reset nb warnings sent counter)
                self._warnings_sent = 0

        if self._warnings_sent < 3 and len(self._daily_missings) > 0:
            print("Error: the following files have not been generated in time:\n %s" % ("\n".join(self._daily_missings)))
            self.send_email(the_dir, self._daily_missings)
        else:
            print("Info: No missing files up to now.")

    def send_email(self, src_dir, errors):
        """
        :param errors: errors msgs describing the missing files
        :return: None
        """
        text = "The following files have not been generated. Please check Cinestsat and datastream on IPPSVAL.\n\nSource dir:%s.\n\n%s" % (src_dir,
            "\n".join(sorted(errors)))

        message = WCMMonitor.MSG_TEMPLATE % (WCMMonitor.FROM, ", ".join(WCMMonitor.TO), WCMMonitor.SUBJECT, text)

        server = smtplib.SMTP(WCMMonitor.SERVER)
        server.sendmail(WCMMonitor.FROM, WCMMonitor.TO, message)
        server.quit()

    def send_daily_report(self, src_dir, the_day):
        """
        :param errors: errors msgs describing the missing files for a complete day
        :return: None
        """

        if len(self._daily_missings) > 0:
            text = "Daily Status for %s.\n The following files have not been generated:\n\nSource dir:%s.\n\n%s" % \
                   (the_day, src_dir, "\n".join(sorted(self._daily_missings)))
        else:
            text = "Daily Status for %s.\n No missing files to report.\n" % the_day

        message = WCMMonitor.MSG_TEMPLATE % (WCMMonitor.FROM, ", ".join(WCMMonitor.TO), "WCM Monitor: Missing Files Summary for %d" % the_day, text)

        server = smtplib.SMTP(WCMMonitor.SERVER)
        server.sendmail(WCMMonitor.FROM, WCMMonitor.TO, message)
        server.quit()

    def send_exception_email(self, err, a_traceback):

        """
        :param errors: errors msgs describing the missing files
        :return: None
        """
        try:
            text = "ERROR. Unforseen exception %s" % (err)

            message = WCMMonitor.MSG_TEMPLATE % (
                WCMMonitor.FROM, ", ".join(["guillaume.aubert@eumetsat.int"]), "Unforseen error on WCM generation Monitor on IPPSVAL", text)

            server = smtplib.SMTP(WCMMonitor.SERVER)
            server.sendmail(WCMMonitor.FROM, WCMMonitor.TO, message)
            server.quit()
        except Exception, email_err:
            tb = traceback.format_exc(err)
            print(
                "%s-Fatal-Error. Cannot send Unforseen exception email. Original error triggering email sending [%s]\nTraceback: %s\n. Error preventing to send the email [%s].\n Traceback: %s\n" % (
                    get_formatted_ts(), err, a_traceback, email_err, tb))


    def run(self):
        """
         run every x minutes as defined in the object (see constructor)
        :return: None
        """
        err_number = 0

        while True:
            try:
                self.monit()

                err_number = 0  # everything is normal
            except Exception, err:
                tb = traceback.format_exc(err)
                print("Error. Received error: [%s].\nTraceback: %s" % (err, tb))
                err_number += 1
                if err_number > 0:
                    self.send_exception_email(err, tb)

            # cannot use finally Python too old
            #finally:

            print("%s-Info: Will now sleep for %s seconds." % (get_formatted_ts()
                , self._sleep_time))
            time.sleep(self._sleep_time)
            print("%s-Info: Wake up at %s" % (
                get_formatted_ts(), datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")))


if __name__ == '__main__':
    # do something
    file_pattern = "MET10_IR108_8bit_%s.csi"
    src_dir_pattern = "/export/home/ipps/cinesat/ape_db/%s/MET10/IR108/8bit"
    sleep_time = 900  # 15 min = 900 seconds

    monitor = WCMMonitor(file_pattern, src_dir_pattern, sleep_time)
    monitor.run()
