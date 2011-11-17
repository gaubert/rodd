'''
Created on Oct 13, 2011

@author: guillaume.aubert@eumetsat.int
'''
from eumetsat.dmon.common.cmdline_utils  import CmdLineParser
from sandbox.batchclient import parse_args

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
    
    parser = CmdLineParser()
    
    parser.add_option("-f", "--from", help = "From datetime (YYYY-MM-DDTHH:MM:SS)", \
                      dest = "from", default ="")
    
    parser.add_option("-u", "--until", \
                      help="Until datetime (YYYY-MM-DDTHH:MM:SS)",\
                      dest="until", default="")
    
    parser.add_option("-n", "--facilities", \
                      help="List of facilities (DVB_EUR_UPLINK, B, C)",\
                      dest="facilities", default="ALL")
    
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
    
    
    
    
    # create the help for the pattern 66 characters is the num do not ask me why ?
    pattern_help  = "Pattern from which the result filenames will be built.".ljust(66)
    pattern_help += "default = {product_name}.".ljust(66)
    pattern_help += "{req_id} : add request id.".ljust(66)
    pattern_help += "{req_filename} :add request filename.".ljust(66)
    pattern_help += "{req_fileprefix} :add request filename prefix.".ljust(66)
    pattern_help += "{req_filesuffix} :add request filename suffix.".ljust(66)
    pattern_help += "{datetime} :add the current local date and time.".ljust(66)
    pattern_help += "{date} :add the current local date.".ljust(66)
    pattern_help += "{time} :add the current local time.".ljust(66)
    pattern_help += "{product_name} :as given by the server.".ljust(66)
    
    parser.add_option("-f", "--file", metavar="FILE", \
                      help = pattern_help, dest="pattern", default="")
     
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
        if options.inline_request:
            parsed_args['mode']          = "inline_request"
            #create a list
            parsed_args['request']       = " ".join(args) 
        else:
            parsed_args['mode']          = "request_file"
            parsed_args['request_files'] = args 
    else:
        # enter interactive mode
        parsed_args['mode']          = 'interactive'
        parsed_args['source']        = sys.stdin
        
    # add output dir
    parsed_args['output_dir']        = options.output_dir 
    
    # add pattern option
    parsed_args['pattern']           = options.pattern
    
    parsed_args['overwrite']         = options.overwrite
    
    parsed_args['no_progress']       = options.no_progress
 
    parsed_args['verbose']           = options.verbose
   
    #check that the pattern is valid
    check_and_replace_pattern(parsed_args['pattern'])
    
    #add parser itself for error handling
    parsed_args['parser'] = parser
    
    return parsed_args



def bootstrap_run():
    """ temporary bootstrap """
    print(parse_args())
   
    
if __name__ == '__main__':
    bootstrap_run()