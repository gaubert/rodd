'''
Created on Jan 14, 2015

@author: guillaume.aubert@eumetsat.int
'''

import datetime

def previous_quater_dt(dt):
    #how many secs have passed this hour
    nsecs = dt.minute*60+dt.second+dt.microsecond*1e-6
    delta = nsecs - (nsecs//900)*900
    #time + number of seconds to quarter hour mark.
    return dt - datetime.timedelta(seconds=delta)

class WCMMonitor(object):

    def __init__(self):
        #do nothing
        pass

    def generate_date_pattern(self):
        """
           generate the date pattern depending on the time
        """
        #get current time
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        t = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime('%y%m%d%H%M')


    def get_list_of_time_since_midnight(the_datetime):
        """
         Return as a datetime the list of 15 min time since midnight.
        """
        result = []
        curr_dt = the_datetime

        first_dt = curr_dt.replace(hour=00, minute=00)

        curr_dt = previous_quater_dt(curr_dt)
        result.append(curr_dt)

        while curr_dt > first_dt:
            curr_dt = previous_quater_dt(curr_dt - datetime.timedelta(minutes=1))
            print("curr_dt = %s" % curr_dt )
            result.append(curr_dt)

        print("result = %s\n" % (result))


if __name__ == '__main__':
    #do something
    get_list_of_time_since_midnight()
