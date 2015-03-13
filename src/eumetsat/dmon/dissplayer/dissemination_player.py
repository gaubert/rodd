__author__ = 'guillaume aubert'

from pytz import utc
import os
import shutil
import datetime
import cPickle as pickle
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
import eumetsat.dmon.parsers.xferlog_parser
import logging

#Load basic config for logging
logging.basicConfig()

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

def copy_job(file_path, destination):
    """
      :return:
    """
    print("%s... Copy %s to %s" % (str(datetime.datetime.now()), file_path, destination['dir']))
    shutil.copy(file_path , destination['dir'])


class DisseminationPlayer(object):

    MIDNIGHT = datetime.time(0,0,0)

    def __init__(self, files_to_parse, index_file, destination):
        """
            :return:
        """
        #ref time = now time plus two minutes
        self._reference_date = datetime.datetime.now() +  datetime.timedelta(seconds=1*60)
        self._parser = eumetsat.dmon.parsers.xferlog_parser.XferlogParser(no_gems_header = True)
        self._files = files_to_parse
        self._scheduler = BlockingScheduler()
        self._index = Indexer.load_index(index_file)
        #destination info (depends on the type of job
        self._destination = destination


    def add_jobs(self):
        """
          Create the jobs from the reference time
        :return:
        """

        for a_file in self._files:
            print("Parsing xferlog file %s" % (a_file) )
            fd = open(a_file)
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
    files = ['e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog/xferlog.saf.txt', 'e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog/xferlog.ears.txt',
             'e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog/xferlog.eps-prime.txt'
            ]
    index_file = 'H:/index.cache'
    destination = { 'dir' : 'e:/IPPS-Data/One-Day-Replay/test-dir' }

    player = DisseminationPlayer(files, index_file, destination)

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



