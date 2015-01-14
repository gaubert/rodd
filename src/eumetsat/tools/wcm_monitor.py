'''
Created on Jan 14, 2015

@author: guillaume.aubert@eumetsat.int
'''
import os
import datetime

def previous_quater_dt(dt):
    #how many secs have passed this hour
    nsecs = dt.minute*60+dt.second+dt.microsecond*1e-6
    delta = nsecs - (nsecs//900)*900
    #time + number of seconds to quarter hour mark.
    return dt - datetime.timedelta(seconds=delta)

class WCMMonitor(object):

    def __init__(self, file_pattern, src_dir):
        #do nothing
        self._file_pattern = file_pattern
        self._src_dir = src_dir

    def generate_date_pattern(self):
        """
           generate the date pattern depending on the time
        """
        #get current time
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        t = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime('%y%m%d%H%M')


    def get_list_of_time_since_midnight(self, the_datetime):
        """
         Return as a datetime the list of 15 min time since midnight.
        """
        result = []
        curr_dt = the_datetime

        first_dt = curr_dt.replace(hour=00, minute=00)

        curr_dt = previous_quater_dt(curr_dt)
        result.append(curr_dt.strftime('%y%m%d%H%M'))

        while curr_dt > first_dt:
            curr_dt = previous_quater_dt(curr_dt - datetime.timedelta(minutes=1))
            #print("curr_dt = %s" % curr_dt )
            result.append(curr_dt.strftime('%y%m%d%H%M'))

        print("result = %s\n" % (result))

        return result

    def monit(self):
        """
        Run the monitoring
        :return: None
        """
        curr_time = datetime.datetime.now()

        missing = []

        #get dir of the current day
        the_day_dir = curr_time.strftime('%y%m%d')

        dates = self.get_list_of_time_since_midnight(curr_time)

        the_dir = "%s/%s" % (self._src_dir, the_day_dir)

        the_files = sorted(os.listdir(the_dir))

        #foreach dates look in the dir if the file is here
        for the_date in sorted(dates):
            filename = file_pattern % (the_date)
            if filename not in the_files:
                print("Error: Missing generation of file %s by Cinesat." % (filename))
                missing.append(filename)

        print("Error: the following files have been generated in time: %s" % (missing))

if __name__ == '__main__':
    #do something
    file_pattern = "myPattern_%s_kkkkk.txt"
    src_dir = "/tmp/test"

    monitor = WCMMonitor(file_pattern, src_dir)

    monitor.monit()
