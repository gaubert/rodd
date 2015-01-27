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

def previous_halfhour_dt(dt):
    # how many secs have passed this hour
    nsecs = dt.minute * 60 + dt.second + dt.microsecond * 1e-6
    delta = nsecs - (nsecs // 1800) * 1800
    # time + number of seconds to quarter hour mark.
    return dt - datetime.timedelta(seconds=delta)

def previous_3hourly(dt):
    """
    :param dt:
    :return:
    """


def get_formatted_ts():
    """
    :return: Formatted Timestamp to go into log messages
    """
    return datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")


class WCMMonitor(object):
    SERVER = "localhost"
    FROM = "wcm_monitor@eumetsat.int"
    #TO = ["guillaume.aubert@eumetsat.int"]
    TO = ["guillaume.aubert@eumetsat.int", "oriol.espanyol@eumetsat.int"]
    SUBJECT = "Potential errors. Data missing on IPPSVAL"

    #formatting must be kept like that
    MSG_TEMPLATE = """\
From: %s
To: %s
Subject: %s

%s
"""

    MAX_WARNINGS_PER_DAY = 1 #nb of emails sent for one file

    WCM_DIR_PATTERN  = "/export/home/ipps/cinesat/ape_export/europe-youtube/%s/%s/%s"
    WCM_FILE_PATTERN = "FRAME_YOUTUBE_108_EUROPE_IR108_%s.jpg"


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
    def get_list_of_time_since_midnight(cls, the_datetime, how_long_before):
        """
         Return as a datetime the list of 15 min time since midnight.
        :rtype : list of time since midnight
        """
        result = []

        # look at the files from - 15 min to let some time for the generation
        curr_dt = the_datetime - datetime.timedelta(minutes= how_long_before)

        first_dt = curr_dt.replace(hour=00, minute=00)

        curr_dt = previous_quater_dt(curr_dt)

        while curr_dt > first_dt:
            curr_dt = previous_quater_dt(curr_dt - datetime.timedelta(minutes=1))
            #print("curr_dt = %s" % curr_dt )
            result.append(curr_dt.strftime('%y%m%d%H%M'))

        return result

    THREE_HOURLY_STEPS = ["WCM_IR_wcm5km_%s%s0000.jpg", "WCM_IR_wcm5km_%s%s0300.jpg", "WCM_IR_wcm5km_%s%s0600.jpg"
                          "WCM_IR_wcm5km_%s%s0900.jpg", "WCM_IR_wcm5km_%s%s1200.jpg", "WCM_IR_wcm5km_%s%s1500.jpg",
                          "WCM_IR_wcm5km_%s%s1800.jpg", "WCM_IR_wcm5km_%s%s2100.jpg"
                         ]

    wcm_step_times = [ datetime.time(1, 0, 00), datetime.time(4, 0, 00), datetime.time(7, 0, 00),
                       datetime.time(10, 0, 00), datetime.time(13, 0, 00), datetime.time(16, 0, 00),
                       datetime.time(19, 0, 00), datetime.time(22, 0, 00) ]

    def monit_wcm(self, the_day):
        """
        Check at the end of the day if the WCM has been generated every 3 hrs
        :return: None
        """
        curr_datetime = datetime.datetime.now()

        # get dir of the current day
        t_day   = curr_datetime.strftime('%d')
        t_month = curr_datetime.strftime('%m')
        t_year  = curr_datetime.strftime('%Y')

        the_dir = self.WCM_DIR_PATTERN % (t_year, t_month, t_day)

        cpt= 0

        #find step
        while  curr_datetime.time() > self.wcm_step_times[cpt] and  cpt < len(self.wcm_step_times):
            cpt +=1

        the_files = sorted(os.listdir(the_dir))

        while  cpt  > 0:
             filename = self.THREE_HOURLY_STEPS[cpt] % ()
             filename = file_pattern % (curr_datetime.strftime('%y'), t_month)
             if filename not in the_files and filename not in self._daily_missings: # file not found
                self._daily_missings.append(filename)
                #new file is missing (reset nb warnings sent counter)
                self._warnings_sent = 0



        #special case around midnight because the target dir is not created before ~ 00:20.
        #only start the monitoring after 00:30.
        thresold_time = datetime.time(0, 30, 0)

        dates = self.get_list_of_time_since_midnight(curr_datetime, 30)

        #send daily report at midnight
        if datetime.time(0, 00, 00) < curr_datetime.time() < datetime.time(0, 15, 00):
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
            self._warnings_sent += 1
        else:
            print("Info: No missing files up to now.")


    def monit(self):
        """
        Run the monitoring
        :return: None
        """
        curr_datetime = datetime.datetime.now()

        # get dir of the current day
        the_day_dir = curr_datetime.strftime('%Y-%m-%d')

        dates = self.get_list_of_time_since_midnight(curr_datetime, 15)

        the_dir = self._src_dir % (the_day_dir)

        #special case around midnight because the target dir is not created before ~ 00:20.
        #only start the monitoring after 00:30.
        thresold_time = datetime.time(0, 30, 0)

        #send daily report at midnight
        if datetime.time(0, 00, 00) < curr_datetime.time() < datetime.time(0, 15, 00):
            yesterday = curr_datetime - datetime.timedelta(days=1)
            self.send_daily_report(the_dir, yesterday.strftime('%Y-%m-%d'))
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

        if self._warnings_sent < self.MAX_WARNINGS_PER_DAY and len(self._daily_missings) > 0:
            print("Error: the following files have not been generated in time:\n %s" % ("\n".join(self._daily_missings)))
            self.send_email(the_dir, self._daily_missings)
            self._warnings_sent += 1
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
            text = "Daily Status for %s.\n No missing files to report.\n" % (the_day)

        message = WCMMonitor.MSG_TEMPLATE % (WCMMonitor.FROM, ", ".join(WCMMonitor.TO), "WCM Monitor: Daily Summary for %s" % (the_day), text)

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
    src_dir_pattern = "/export/home/ipps/cinesat/ape_db/%s-%s-%s/MET10/IR108/8bit"

    wcm_dir_pattern  = "/export/home/ipps/cinesat/ape_export/europe-youtube/%s/%s/%s"
    wcm_file_pattern = "FRAME_YOUTUBE_108_EUROPE_IR108_%s.jpg"

    sleep_time = 900  # 15 min = 900 seconds

    monitor = WCMMonitor(file_pattern, src_dir_pattern, sleep_time)
    monitor.run()
