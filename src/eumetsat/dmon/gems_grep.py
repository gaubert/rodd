'''
Created on Oct 13, 2011

@author: guillaume.aubert@eumetsat.int
'''

import datetime
import eumetsat.dmon.common.time_utils as time_utils
from eumetsat.dmon.common.cmdline_utils  import CmdLineParser

import eumetsat.dmon.gems_feeder as gems_feeder


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

ALL_KWD = 'ALL'

class GEMSGrep(object):
    
    def __init__(self):
        """ constructor """
        super(GEMSGrep, self).__init__()

    def parse_args(self):
        """ Parse command line arguments 
            
            :returns: a dict that contains the arguments
               
            :except Exception Error
            
        """
        #print sys.argv
        
        parser = CmdLineParser()
        
        parser.add_option("-f", "--from", help = "From datetime (YYYY-MM-DDTHH:MM:SS)", \
                          dest = "dfrom", default = None)
        
        parser.add_option("-u", "--until", \
                          help="Until datetime (YYYY-MM-DDTHH:MM:SS)",\
                          dest="duntil", default= None)
        
        parser.add_option("-n", "--facilities", \
                          help="List of facilities (DVB_EUR_UPLINK, DVB_CBAND_SAM)",\
                          dest="facilities", default=None)
        
        parser.add_option("-m", "--hosts", \
                          help="filter by hosts if necessary",\
                          dest="hosts", default="ALL")
     
        parser.add_option("-v", "--verbose", \
                          help="Activate the verbose mode.",\
                          action="store_true", dest="verbose", default=False)
       
        """
        dir_help =  "Directory where the result files will be stored.".ljust(66)
        dir_help += "(Default =. the current dir)".ljust(66)
        dir_help += "The directory will be created if it doesn't exist.".ljust(66)
        
        parser.add_option("-d", "--dir", metavar="DIR", \
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
        
        # enter request_file mode       
        if len(args) > 0:
            #create a list of grep elements
            parsed_args['search_request']       = " ".join(args) 
        
        # if file check that file exist and read it
        # otherwise if -i read stdin 
        # otherwise start interactive session
            
        # add from
        parsed_args['from']              = options.dfrom
        
        # add until
        parsed_args['until']             = options.duntil
        
        #facilities
        parsed_args['facilities']        = options.facilities
        
        #hosts
        parsed_args['hosts']             = options.hosts
     
        #verbose
        parsed_args['verbose']           = options.verbose
        
        #add parser itself for error handling
        parsed_args['parser'] = parser
        
        return parsed_args
    
    def _parse_facilities(self, str_facilities):
        """
           create list of facilities 
        """
        return [fac.strip() for fac in str_facilities.split(",")]
        
    
    def _process_facilities(self, args):
        """
           Check the facilities
        """
        str_facilities = args.get("facilities", None)
        
        facilities = []
        
        if not str_facilities:
            #for the moment use this default but a default list 
            #should be built from the GEMS facilities list
            #keep only the first facilities as default at the moment
            facilities = [ gems_feeder.GEMSExtractor.get_all_GEMS_facilities()[0] ]
        else:
            #ask for a search in all facilities (dangerous ?)
            if str_facilities == ALL_KWD:
                facilities = gems_feeder.GEMSExtractor.get_all_GEMS_facilities()
            else:
                facilities = self._parse_facilities(str_facilities)
            
        return facilities
        

    def _process_dates(self, args):
        """ 
            Do the date checkings  and convert them to date time.
            If no dates are provided define an interval of from = now - 1hours and until = now
            
            :Return a tuple (dfrom, duntil)
        """
        
        dfrom  = args.get('from', None)
        duntil = args.get('until', None)
        
        now = datetime.datetime.utcnow()
        
        if dfrom:
            dfrom  = time_utils.convert_date_str_to_datetime(dfrom)
        else:
            #set default for from: create datetime now - 1 hours
            dfrom =  now + datetime.timedelta(hours=-1)
        
        if duntil:
            #set default for until: create datetime now 
            duntil = time_utils.convert_date_str_to_datetime(duntil)
        else:
            #create datetime now 
            duntil = now 
        
        
        #check that from is anterior to until
        if dfrom >= duntil:
            raise Exception("from date (%s) cannot be posterior to until date (%s)" %(args.get('from', None), args.get('until', None)))
        
        return (dfrom, duntil)
    
    def run(self, args):
        """
           Run the grep with the given args 
        """
        dfrom, duntil =  self._process_dates(args)
    
        facilities    =  self._process_facilities(args)
        
        extractor     =  gems_feeder.GEMSExtractor(start_time = dfrom, end_time = duntil, facility = facilities, search ='tc-send')
        
        for data_dict in extractor:
            
            fac  = data_dict['facility']
            dt = time_utils.convert_date_str_to_datetime(data_dict['time'])
            time = time_utils.datetime_to_compactdate(dt)
            msg  = data_dict['msg']
            
            print('%s %s %s' %(fac, time , msg))
    
def bootstrap_run():
    """ temporary bootstrap """
    
    gems_grep = GEMSGrep()
    
    args = gems_grep.parse_args()
    
    gems_grep.run(args)
   
    
if __name__ == '__main__':
    import sys
    sys.argv = ['/homespace/gaubert/ecli-workspace/rodd/src/eumetsat/dmon/gems_grep.py', '--from', '2011-04-03T14:30:00', '--until', '2011-05-04T14:40:00', "dmon.log"]
    
    print(sys.argv)
    
    bootstrap_run()
    
    sys.exit(0)