from datetime import datetime
import time
from apscheduler.scheduler import Scheduler

import upload_ftp

config = {'daemonic': True}

# Start the scheduler
sched = Scheduler(config)

# Define the function that is to be executed
def puma_job(text):
    filename='todo.txt'
    server='xxxxxxxxxxx'
    login='xxxxxxxxxx' # look into /home/Aubert/Dev/python for the login details
    passwd='xxxxxxxxx'
    directory='xxxxxxxxxxxx'
    print("Start Job Upload PUMA Patch\n")
    upload_ftp.upload(filename,server,login,passwd,directory)
    print("End of Job Upload PUMA Patch\n")

    print("Scheduler enters in sleep mode again")

# Define the function that is to be executed
def puma1_job(text):
    filename='todo.txt'
    server='oisftp.eumetsat.int'
    login='xxxxxxxxxxxx'
    passwd='xxxxxxxxxxx'
    directory='xxxxxxxxxxx'
    print("Start Job Upload PUMA1 Patch\n")
    upload_ftp.upload(filename,server,login,passwd,directory)
    print("End of Job Upload PUMA1 Patch\n")

    print("Scheduler enters in sleep mode again")

# The job will be executed on November 6th, 2009
exec_date = datetime(2011,9,30, 17, 14, 30)

# Store the job in a variable in case we want to cancel it
print("Registering Job puma_job\n")
job = sched.add_date_job(puma_job, exec_date, ['text'])

# The job will be executed on November 6th, 2009
exec_date = datetime(2011,9,30, 17, 16, 30)

# Store the job in a variable in case we want to cancel it
print("Registering Job puma_job1\n")
job = sched.add_date_job(puma1_job, exec_date, ['text'])

print("List of REgistered jobs")
sched.print_jobs()

sched.start()

# wait for ever as it is a daemon
print("Start Waiting ....")
while True:
   time.sleep(300)

