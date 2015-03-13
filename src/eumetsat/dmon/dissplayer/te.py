__author__ = 'Aubert'

from pytz import utc
import datetime
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.util import undefined


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=10)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

def runnable(file_path):
    """

    :return:
    """
    # run a job
    print("JOB now starting. FIle path %s" % (file_path))
    print("JOB .....")
    print("JOB now finished")

scheduler = BlockingScheduler()

# .. do something else here, maybe add jobs etc.

the_date = datetime.datetime.now() +  datetime.timedelta(seconds=2)

d_trigger = DateTrigger(the_date)

l = lambda: runnable('/tmtmtmtmtmtmt')

scheduler.add_job(func=runnable, trigger=d_trigger, args=['tick\n'])

the_date = datetime.datetime.now() +  datetime.timedelta(seconds=2)

d_trigger = DateTrigger(the_date)

scheduler.add_job(func=runnable, trigger=d_trigger, args=['tick1\n'])

scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

scheduler.start()