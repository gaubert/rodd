'''
Created on Jun 15, 2011

@author: guillaume.aubert@gmail.com
'''

import subprocess
import signal
import os
import select
import fcntl
import time

class WMCTRLHelper(object): # pylint: disable-msg=R0903
    """ Python Helper calling WMCTRL executable:
    """
    
    ERROR_PREFIX = "ERROR:"
    INFO_PREFIX  = "INFO:"
    DEBUG_PREFIX = "DEBUG:"
    
    def __init__(self):
        """ constructor """
        pass
    
    @classmethod
    def _set_flags(cls, a_proc):
        """ Set non blocking flags for the process stdout and stderr
        """
        # get fd flags for stdout and stderr and make them non-blocking
        flags = fcntl.fcntl(a_proc.stdout, fcntl.F_GETFL)
        if not a_proc.stdout.closed:
            fcntl.fcntl(a_proc.stdout, fcntl.F_SETFL, flags| os.O_NONBLOCK)
        
        flags = fcntl.fcntl(a_proc.stderr, fcntl.F_GETFL)
        if not a_proc.stderr.closed:
            fcntl.fcntl(a_proc.stderr, fcntl.F_SETFL, flags| os.O_NONBLOCK)
            
    def active_window_north_east(self, a_timeout = 10800):
        """ send active windows to north east corner """
        command="/homespace/gaubert/bin/wmctrl -r :ACTIVE: -e 1,960,580,950,580"
        
        #execute process 
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env= self._get_env())
        
        WMCTRLHelper._set_flags(proc)
            
        inputs = [proc.stdout, proc.stderr]
            
        reading_on_stdout = True
        reading_on_stderr = True
               
        #time limit in seconds
        limit = time.time() + a_timeout
        
        while reading_on_stdout or reading_on_stderr:
            
            # the select will block for up to select_timeout seconds before to come back 
            inputready, _, _ = select.select(inputs, [], [], self._select_timeout)
            
            #if we have reached the time limit for the process quit in error
            if time.time() > limit:
                # when using 2.6 call terminate and kill maybe
                #p.terminate()
                WMCTRLHelper._kill_process(proc.pid)
                return (15,"ERROR: The request is still running after %d sec. Abort in error.")
        
            for src_fd in inputready:
                if src_fd == proc.stdout:
                    # handle the server socket
                    buf = src_fd.read(self._buffer_size)
                    a_dest_fd.write(buf)
                    #nothing else to read => stdout is closed and the processed is finished
                    if not buf:
                        proc.stdout.close()
                        reading_on_stdout = False
                        inputs.remove(proc.stdout)
                        
                elif src_fd == proc.stderr:
                    buf = src_fd.read(self._buffer_size)
                    user_info.append(buf)
                    #nothing else to read => stdout is closed and the processed is finished
                    if not buf:
                        proc.stderr.close()
                        reading_on_stderr = False
                        inputs.remove(proc.stderr)

        # for the moment wait for ever (will have find a way to kill the process if necessary)
        retval = proc.wait()
        
        self._logger.info("returned value %d" % (retval) )
        
        return retval, user_info
        
    def get_wave_data(self, a_dest_fd, a_stations_dict, a_begin, a_end, a_format, a_timeout = 10800):#pylint:disable-msg=R0913,R0914
        """ Get one option from a section.
        
            return the default if it is not found and if fail_if_missing is False, otherwise return NoOptionError
          
            :param a_dest_fd: file descriptor where the data is going to be written
            :param a_stations_dict: A dictionnary containing stations (key) and a list of related channels (value)
            :type  section: dictionnary
            :param a_begin: begin date
            :type  section: date
            :param a_end: end date
            :type  section: str
            :param a_format: returned format (INT | CM6 | CSF | RAW)
            :type  section: str
            :param a_timeout: timeout after which this method should come back (default 3hrs (10800 seconds))
            :type  section: str
 
            :returns: the option as a string
            
            :except NoOptionError: Raised only when fail_is_missing set to True
        
        """
        
        #information returned to the user
        user_info = []
        
        command = self._build_command(a_stations_dict, a_begin, a_end, a_format)
        
        #execute process 
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env= self._get_env())
        
        WMCTRLHelper._set_flags(proc)
            
        inputs = [proc.stdout, proc.stderr]
            
        reading_on_stdout = True
        reading_on_stderr = True
               
        #time limit in seconds
        limit = time.time() + a_timeout
        
        while reading_on_stdout or reading_on_stderr:
            
            # the select will block for up to select_timeout seconds before to come back 
            inputready, _, _ = select.select(inputs, [], [], self._select_timeout)
            
            #if we have reached the time limit for the process quit in error
            if time.time() > limit:
                # when using 2.6 call terminate and kill maybe
                #p.terminate()
                WaveReaderHelper._kill_process(proc.pid)
                return (15,"ERROR: The request is still running after %d sec. Abort in error.")
        
            for src_fd in inputready:
                if src_fd == proc.stdout:
                    # handle the server socket
                    buf = src_fd.read(self._buffer_size)
                    a_dest_fd.write(buf)
                    #nothing else to read => stdout is closed and the processed is finished
                    if not buf:
                        proc.stdout.close()
                        reading_on_stdout = False
                        inputs.remove(proc.stdout)
                        
                elif src_fd == proc.stderr:
                    buf = src_fd.read(self._buffer_size)
                    user_info.append(buf)
                    #nothing else to read => stdout is closed and the processed is finished
                    if not buf:
                        proc.stderr.close()
                        reading_on_stderr = False
                        inputs.remove(proc.stderr)

        # for the moment wait for ever (will have find a way to kill the process if necessary)
        retval = proc.wait()
        
        self._logger.info("returned value %d" % (retval) )
        
        return retval, user_info
    
    @classmethod
    def _kill_process(cls, a_pid):
        """
           Send a SIGTERM signal to the process.
           :param a_pid: pid of the process.
           
        """
        os.kill(a_pid, signal.SIGTERM)
        #os.kill(a_pid, signal.SIGKILL)
        
    def _get_env(self):
        """ 
           Create the environement for the child process 
           
           :returns: return the created env 
           
        """
        
        # there is a bug in libparidc that makes waveReader bomb when it is launched with subprocess
        # The size of the environment seems to be limited and it makes libparidc bombing.
        # the code in this library seems to be failry dangerous and shaky
        
        the_env = {
                   # add this to force libparidc not trying to load the env for the waveReader to avoid crash
                   "NOENV": "1", 
                   # get TNS_ADMIN for the current process
                   "TNS_ADMIN" : os.environ.get('TNS_ADMIN','ERROR_NOT_SET'), 
                   # get ORACLE_HOME from the current process
                   "ORACLE_HOME" : os.environ.get('ORACLE_HOME','ERROR_NOT_SET'),
                   # get LD_LIBRARY_PATH to load the oracle libs
                   "LD_LIBRARY_PATH": os.environ.get('LD_LIBRARY_PATH','ERROR_NOT_SET'),
                  }
        
        return the_env



if __name__ == '__main__':
    pass