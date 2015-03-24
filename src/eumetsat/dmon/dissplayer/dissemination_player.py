__author__ = 'guillaume aubert'

from pytz import utc
import os
import sys
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
from apscheduler.executors.pool import ThreadPoolExecutor
import logging

import eumetsat.dmon.common.utils as utils
import eumetsat.dmon.common.cmdline_utils as cmdline_utils
import eumetsat.dmon.parsers.xferlog_parser


#Load basic config for logging
logging.basicConfig()

jobstores = {
#    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
    'default': MemoryJobStore()
}
executors = {
    #'default': {'type': 'processpool', 'max_workers': 20},
    'default': ThreadPoolExecutor(max_workers=20),
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

    def __init__(self, top_data_dir, index_file, dir_files_to_parse, files_to_parse, job_func, destination):
        """
            :return:
        """
        self._parser = eumetsat.dmon.parsers.xferlog_parser.XferlogParser(no_gems_header = True)
        self._dir_files = dir_files_to_parse
        self._files = files_to_parse
        self._job_func = job_func
        self._scheduler = BlockingScheduler()

        res = []
        t = ftimer(Indexer.load_index, [top_data_dir, index_file], {}, res)
        print("Read index in %d seconds." % (t))
        self._index = res[0]

        #can now set reference time
        #ref time = now time plus one minute
        self._defer_time = 5 
        self._reference_date = datetime.datetime.now() +  datetime.timedelta(seconds=self._defer_time)

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

        print("Start Scheduler. Jobs will start to be played in %d sec." % self._defer_time)
        self._scheduler.start()


class Indexer(object):
    """
       Build a file to file path index in order to be quick
    """

    def __init__(self):
        """
           :return:
        """

    @classmethod
    def load_index(self, top_data_dir, index_file_path, recreate = False):
        """
           Load or Create the index if a cache file doesn't exist
        :return:
        """
        cache = {}
        if recreate or not os.path.exists(index_file_path):
            print("File Indexer. Create an index file %s to fastly access all data files from %s. It might take few minutes." % (index_file_path, top_data_dir))
            fd = open(index_file_path, "w")
            for path, _, files in os.walk(top_data_dir):
                for filename in files:
                    filepath = os.path.join(path, filename)
                    cache[filename] = filepath

            print("File Indexer. Store index in %s." % (index_file_path))

            pickle.dump(cache, open(index_file_path, "wb"))

            print("File Indexer. Indexed created.")
        else:
            print("File Index. Load index from %s." % (index_file_path))
            cache = pickle.load( open( index_file_path, "rb" ) )
            print("File Indexer. Index loaded")

        return cache



def read_configuration_file(a_filepath):
    """
    Read the configuration file
    :param a_filepath:
    :return:
    """

    if os.path.exists(a_filepath):
        json_data=open(a_filepath)
        data = json.load(json_data)
    else:
        raise Exception("Error. Configuration file %s doesn't exist." % (a_filepath) )

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

    try:
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
    except Exception, e:
        tracebk = utils.get_exception_traceback()
        print(e)
        print("Traceback %s" % (tracebk))
        sys.exit(1)

    sys.exit(0)

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



class SimpleException(Exception):
    """
       Simple exception that will not require to print the stack trace, ie. CommandLine argument missing, ....
    """
    pass

HELP_USAGE = """ diss_player --conf conf_filepath

Replay dissemination xferlogs.
Arguments: None"""

HELP_EPILOGUE = """Examples:

a) diss_player --conf /tmp/myconf.json

Examples of conf file:

cp_job example:
{
  "job_type" : "cp_job",
  "xferlog_dir"  : "e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog",
  "files" : ["xferlog.ears.txt"],
  "top_data_dir" : "e:/IPPS-Data/One-Day-Replay/data/20150311-data",
  "index_file" : "H:/index.cache",
  "destination" : { "dest-dir" : "e:/IPPS-Data/One-Day-Replay/test-dir" }
}

scp_job example:
{
  "job_type" : "scp_job",
  "xferlog_dir"  : "e:/IPPS-Data/One-Day-Replay/xferlog-lftp/xferlog",
  "files" :  ["xferlog.dwd.txt", "xferlog.ears.txt", "xferlog.eps-prime.txt", "xferlog.hrit-0.txt", "xferlog.hrit-rss.txt", "xferlog.other.txt",
             "xferlog.saf.txt", "xferlog.saflsa.txt", "xferlog.safo3m.txt", "xferlog.wmora1.txt", "xferlog.wmora6.txt"
             ] ,
  "top_data_dir" : "e:/IPPS-Data/One-Day-Replay/data/20150311-data"
  "index_file" : "H:/index.cache",
  "destination" : { "scp": "C:/Users/Aubert/AppData/Local/Temp/Aubert_MobaXterm6.5/bin/scp" , "user" : "gaubert", "host" : "tclxs10", "dest-dir" : "/tcc1/home/gaubert/test-dir" }
}

With:
 - job_type    : Type of job executed by the scheduler. It can be a cp_job or a scp_job.
                 Each job_type takes a different individual destination argument.
 - xferlog_dir : Directory where the xferlog files to re-play are.
 - files       : list of xferlog files to replay.
 - top_data_dir: top directory containing all data files.
 - index_file  : index file that contains the file -> file_path list to avoid find and ls commands for getting the data.
 - destination : information related to the destination that depends on the job_type.
 - defer_time  : reference time for the scheduler. It is the time zero after which the files are played. If not provide it is 5 seconds.

"""

def parse_args():
        """ Parse command line arguments

            :returns: a dict that contains the arguments

            :except Exception Error

        """
        #print sys.argv

        parser = cmdline_utils.CmdLineParser()

        parser.add_option("-c", "--conf", help = "configuration file path in json. See help for conf file examples.", \
                          dest = "dconf", default = None)

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

        #add parser itself for error handling
        parsed_args['parser'] = parser

        return parsed_args

def run_cmd():
    """
    Run the command
    :return:
    """
    j_type = None

    parsed_args = parse_args()

    if not parsed_args['conf_path']:
        print("Error. Need a configuration file. diss_player -h for more information.")
        parsed_args['parser'].die_with_usage()

    try:
        conf = read_configuration_file(parsed_args['conf_path'])

        if conf["job_type"] == "cp_job":
            j_type = cp_job
        elif conf["job_type"] == "scp_job":
            j_type = scp_job
        else:
            raise SimpleException("Error. Unknown job type %s" % (conf["job_type"]))

        player = DisseminationPlayer(conf['top_data_dir'], conf['index_file'], conf['xferlog_dir'], conf['files'] , j_type, conf['destination'])

        player.add_jobs()

        player.start()
    except SimpleException, se:
        print(se)
        parsed_args['parser'].die_with_usage()
    except Exception, e:
        tracebk = utils.get_exception_traceback()
        print(e)
        print("Traceback %s" % (tracebk))
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':

    #test_parser()
    #test_index()
    run_cmd()



