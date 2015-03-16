__author__ = 'guillaume aubert'

from pytz import utc
import os
import itertools
import gc
import time
import shutil
import datetime
import cPickle as pickle
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
import eumetsat.dmon.parsers.xferlog_parser
import logging

#Load basic config for logging
logging.basicConfig()

jobstores = {
#    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    'default': MemoryJobStore()
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=10)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

def ftimer(func, args, kwargs, result = [], number=1, timer=time.time): #IGNORE:W0102
    """ time a func or object method """
    it = itertools.repeat(None, number)
    gc_saved = gc.isenabled()

    try:
        gc.disable()
        t0 = timer()
        for i in it:                  #IGNORE:W0612
            r = func(*args, **kwargs) #IGNORE:W0142
            if r is not None:
                result.append(r)
                t1 = timer()
    finally:
        if gc_saved:
            gc.enable()

    return t1 - t0

def copy_job(file_path, destination):
    """
      :return:
    """
    print("%s... Copy %s to %s" % (str(datetime.datetime.now()), file_path, destination['dir']))
    shutil.copy(file_path , destination['dir'])


class DisseminationPlayer(object):

    MIDNIGHT = datetime.time(0,0,0)

    def __init__(self, dir_files_to_parse, files_to_parse, index_file, destination):
        """
            :return:
        """
        #ref time = now time plus two minutes
        self._reference_date = datetime.datetime.now() +  datetime.timedelta(seconds=2*60)
        self._parser = eumetsat.dmon.parsers.xferlog_parser.XferlogParser(no_gems_header = True)
        self._dir_files = dir_files_to_parse
        self._files = files_to_parse
        self._scheduler = BlockingScheduler()

        res = []
        t = ftimer(Indexer.load_index, [index_file], {}, res)
        print("read index in %d" % (t))
        self._index = res[0]

        #destination info (depends on the type of job
        self._destination = destination


    def add_jobs(self):
        """
          Create the jobs from the reference time
        :return:
        """

        for a_file in self._files:
            f_path = "%s/%s" % (self._dir_files, a_file)
            print("Parsing xferlog file %s" % f_path )
            fd = open(f_path)
            self._parser.set_lines_to_parse(fd)
            for elem in self._parser:
                #print("time = %s, filename = %s\n" % (elem['time'], elem['file']))
                #find file in index
                filepath = self._index.get(elem['file'], None)
                if filepath:
                    #get time difference
                    midnight_date = utc.localize(datetime.datetime.combine(elem['time'].date(), self.MIDNIGHT))
                    #print("midnight date = %s ///// elem[time] = %s" % (midnight_date, elem['time']))
                    time_diff = elem['time'] - midnight_date
                    scheduled_date = self._reference_date + time_diff
                    #create job and schedule it with the time difference added to the starting reference time
                    d_trigger = DateTrigger(scheduled_date)

                    self._scheduler.add_job(copy_job, d_trigger, args=[filepath, self._destination])
                else:
                    print("Could not find %s\n in Index" % (elem['file']))

        print("Player. %d jobs scheduled.\n" % (len(self._scheduler.get_jobs())))


    def start(self):
        """
        :return:
        """
        self._scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)

        print("Start Scheduler")
        self._scheduler.start()


class Indexer(object):
    """
       Build a file to file path index in order to be quick
    """

    def __init__(self, top_dir, cache_file):
        """
           :return:
        """
        self._top_dir = top_dir
        self._cache_file_path = cache_file

    def create_index(self, recreate = False):
        """
           Create the index if a cache file doesn't exist
        :return:
        """
        cache = {}
        if recreate or not os.path.exists(self._cache_file_path):
            print("Index. Will create the index. It might take a long time.")
            fd = open(self._cache_file_path, "w")
            for path, _, files in os.walk(self._top_dir):
                for filename in files:
                    filepath = os.path.join(path, filename)
                    cache[filename] = filepath

            print("Index. Store index in %s." % (self._cache_file_path))

            pickle.dump(cache, open(self._cache_file_path, "wb"))

            print("Index. Indexed cached.")
        else:
            print("Index. Load index from %s." % (self._cache_file_path))
            cache = pickle.load( open( self._cache_file_path, "rb" ) )
            print("Index. Index loaded")

        return cache

    @classmethod
    def load_index(cls, index_file):
        """
        """
        print("Index. Load index from %s." % (index_file))
        index = pickle.load( open( index_file, "rb" ) )
        print("Index. Index loaded")
        return index


def test_index():
    """

    :return:
    """
    """
    :return:
    """
    top_dir = "e:/IPPS-Data/One-Day-Replay/data/20150311-data/EPS-3"
    cache_file = "H:/index1.cache"

    indexer = Indexer(top_dir, cache_file)

    print("Create Index")
    index = indexer.create_index(recreate = False)

    #for key in index:
    #    print("key = %s, val = %s" % (key, index[key]))

    print("Index created")

def test_player():
    """

    :return:
    """
    xferlog_dir = 'e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog'

    files = ['xferlog.dwd.txt', 'xferlog.ears.txt', 'xferlog.eps-prime.txt', 'xferlog.hrit-0.txt', 'xferlog.hrit-rss.txt', 'xferlog.other.txt',
             'xferlog.saf.txt', 'xferlog.saflsa.txt', 'xferlog.safo3m.txt', 'xferlog.wmora1.txt', 'xferlog.wmora6.txt'

            ]
    index_file = 'H:/index.cache'
    destination = { 'dir' : 'e:/IPPS-Data/One-Day-Replay/test-dir' }

    player = DisseminationPlayer(xferlog_dir, files, index_file, destination)

    player.add_jobs()

    player.start()

def test_parser():
    """

    :return:
    """
    fd = open('e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog/xferlog.other.txt')
    parser = eumetsat.dmon.parsers.xferlog_parser.XferlogParser(no_gems_header = True)
    parser.set_lines_to_parse(fd)
    for elem in parser:
        print("time = %s, filename = %s\n" % (elem['time'], elem['file']))

if __name__ == '__main__':

    #test_parser()
    #test_index()
    test_player()



