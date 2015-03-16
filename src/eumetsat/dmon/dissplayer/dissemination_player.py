__author__ = 'guillaume aubert'

from pytz import utc
import os
import itertools
import gc
import time
import shutil
import datetime
import subprocess
import json
import cPickle as pickle
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
#from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
import logging

import eumetsat.dmon.common.cmdline_utils as cmdline_utils
import eumetsat.dmon.parsers.xferlog_parser


#Load basic config for logging
logging.basicConfig()

jobstores = {
#    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    'default': MemoryJobStore()
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=20)
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

def cp_job(file_path, destination):
    """
      :return:
    """
    print("%s... cp %s to %s" % (str(datetime.datetime.now()), file_path, destination['dest-dir']))
    shutil.copy(file_path , destination['dest-dir'])

def scp_job(file_path, destination):
    """
      :return:
    """
    print("%s... %s %s %s@%s:%s" % (str(datetime.datetime.now()), destination['scp'], file_path, destination['user'], destination['host'], destination['dest-dir']))
    subprocess.Popen([destination['scp'], file_path, "%s@%s:%s" % (destination['user'], destination['host'], destination['dest-dir'])]).wait()


class DisseminationPlayer(object):

    MIDNIGHT = datetime.time(0,0,0)

    def __init__(self, dir_files_to_parse, files_to_parse, index_file, job_func, destination):
        """
            :return:
        """
        #ref time = now time plus two minutes
        self._reference_date = datetime.datetime.now() +  datetime.timedelta(seconds=30)
        self._parser = eumetsat.dmon.parsers.xferlog_parser.XferlogParser(no_gems_header = True)
        self._dir_files = dir_files_to_parse
        self._files = files_to_parse
        self._job_func = job_func
        self._scheduler = BlockingScheduler()

        res = []
        t = ftimer(Indexer.load_index, [index_file], {}, res)
        print("Read index in %d seconds." % (t))
        self._index = res[0]

        #destination info (depends on the type of job)
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

                    self._scheduler.add_job(self._job_func, d_trigger, args=[filepath, self._destination])
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


def read_configuration_file(a_filepath):
    """
    Read the configuration file
    :param a_filepath:
    :return:
    """
    json_data=open(a_filepath)
    data = json.load(json_data)

    return data

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

def test_player_with_cp():
    """

    :return:
    """

    #xferlog_dir = 'e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog'

    #files = ['xferlog.dwd.txt', 'xferlog.ears.txt', 'xferlog.eps-prime.txt', 'xferlog.hrit-0.txt', 'xferlog.hrit-rss.txt', 'xferlog.other.txt',
    #         'xferlog.saf.txt', 'xferlog.saflsa.txt', 'xferlog.safo3m.txt', 'xferlog.wmora1.txt', 'xferlog.wmora6.txt'

    #files = ['xferlog.ears.txt']

    #index_file = 'H:/index.cache'
    #destination = { 'dest-dir' : 'e:/IPPS-Data/One-Day-Replay/test-dir' }

    conf = read_configuration_file("C:/Dev/ecli-workspace/rodd/etc/diss-player/cp_test.json")

    j_type = None

    if conf["job_type"] == "cp_job":
        j_type = cp_job
    elif conf["job_type"] == "scp_job":
        j_type = scp_job
    else:
        raise Exception("Error. Unknown job type %s" % (conf["job_type"]))

    player = DisseminationPlayer(conf['xferlog_dir'], conf['files'] , conf['index_file'], j_type, conf['destination'])

    player.add_jobs()

    player.start()

def test_player_with_scp():
    """

    :return:
    """
    xferlog_dir = 'e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog'

    files = ['xferlog.dwd.txt', 'xferlog.ears.txt', 'xferlog.eps-prime.txt', 'xferlog.hrit-0.txt', 'xferlog.hrit-rss.txt', 'xferlog.other.txt',
             'xferlog.saf.txt', 'xferlog.saflsa.txt', 'xferlog.safo3m.txt', 'xferlog.wmora1.txt', 'xferlog.wmora6.txt'
            ]

    files = ['xferlog.ears.txt']

    index_file = 'H:/index.cache'
    destination = { 'scp': 'C:\Users\Aubert\AppData\Local\Temp\Aubert_MobaXterm6.5\bin\scp' , 'user' : 'gaubert', 'host' : 'tclxs10', 'dest-dir' : '/tcc1/home/gaubert/test-dir' }

    player = DisseminationPlayer(xferlog_dir, files, index_file, scp_job, destination)

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


HELP_USAGE = """ nms_client [options] request files or request

Arguments: a list of request files or an inline request."""

HELP_EPILOGUE = """Examples:

a) Requests examples

- Retrieve shi data with a request stored in a file
#> nms_client ims_shi.req

b) Pattern examples

#> nms_client shi.req -f "{req_id}_{req_fileprefix}.data"
will create 546_shi.data.

#> nms_client shi.req -f "{req_id}_{date}.data"
will create 547_20091224.data.

#> nms_client shi.req -f "{req_id}_{datetime}.data"
will create 548_20091224-01h12m23s.data

#> nms_client shi-1.req shi-2.req -f "{req_id}_{req_fileprefix}.data"
will create 549_shi-1.data and 550_shi-2.data
"""

def parse_args():
        """ Parse command line arguments

            :returns: a dict that contains the arguments

            :except Exception Error

        """
        #print sys.argv

        parser = cmdline_utils.CmdLineParser()

        parser.add_option("-c", "--conf", help = "configuration file path in json", \
                          dest = "dconf", default = None)

        """
        dir_help =  "Directory where the result files will be stored.".ljust(66)
        dir_help += "(Default =. the current dir)".ljust(66)
        dir_help += "The directory will be created if it doesn't exist.".ljust(66)

        parsers.add_option("-d", "--dir", metavar="DIR", \
                          help = dir_help,\
                          dest ="output_dir", default=".")
        """

        # add custom usage and epilogue
        parser.epilogue = HELP_EPILOGUE
        parser.usage    = HELP_USAGE

        (options, args) = parser.parse_args() #pylint: disable-msg=W0612

        parsed_args = { }

        # if file check that file exist and read it
        # otherwise if -i read stdin
        # otherwise start interactive session


        # add from
        parsed_args['conf_path']              = options.dconf

        #add parsers itself for error handling
        parsed_args['parsers'] = parser

        return parsed_args

def run_cmd():
    """
    Run the command
    :return:
    """
    j_type = None

    parsed_args = parse_args()

    conf = read_configuration_file(parsed_args['conf_path'])

    if conf["job_type"] == "cp_job":
        j_type = cp_job
    elif conf["job_type"] == "scp_job":
        j_type = scp_job
    else:
        raise Exception("Error. Unknown job type %s" % (conf["job_type"]))

    player = DisseminationPlayer(conf['xferlog_dir'], conf['files'] , conf['index_file'], j_type, conf['destination'])

    player.add_jobs()

    player.start()


if __name__ == '__main__':

    #test_parser()
    #test_index()
    run_cmd()



