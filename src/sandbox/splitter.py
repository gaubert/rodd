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
import re

class WMCTRLHelper(object): # pylint: disable-msg=R0903
    """ Python Helper calling WMCTRL executable:
    """
    
    ERROR_PREFIX = "ERROR:"
    INFO_PREFIX  = "INFO:"
    DEBUG_PREFIX = "DEBUG:"
    
    def __init__(self, buffer_size, select_timeout,base_command):
        """ constructor """
        self._buffer_size     = buffer_size
        self._select_timeout  = select_timeout
        self._command         = base_command 
        self._desktop_dimensions = None
    
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
            
    def _generate_wmctrl_command_line(self, x, y, width, height):
        """
          wmctlr -r :ACTIVE: -e 1,x,y,width,height.
          example "/bin/wmctrl -r :ACTIVE: -e 1,960,580,950,580"
        """
        
        return "%s -r :ACTIVE: -e 1,%s,%s,%s,%s" % (self._command, x, y, width, height)
        
    def create_move_to_full_screen_command(self):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = 0
        y_pos   = 0
        width   = self._desktop_dimensions["width"]
        height  = self._desktop_dimensions["height"]
        
        return self._generate_wmctrl_command_line(x_pos, y_pos, width, height)
            
    def create_move_to_window_north_east_command(self):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = self._desktop_dimensions["width"] / 2
        y_pos   = 0
        width   = self._desktop_dimensions["width"] / 2
        height  = self._desktop_dimensions["height"] / 2
        
        return self._generate_wmctrl_command_line(x_pos, y_pos, width, height)
    
    def create_move_to_window_north_west_command(self):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = 0
        y_pos   = 0
        width   = self._desktop_dimensions["width"] / 2
        height  = self._desktop_dimensions["height"] / 2
        
        return self._generate_wmctrl_command_line(x_pos, y_pos, width, height)
    
    def create_move_to_window_east_command(self):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = self._desktop_dimensions["width"] / 2
        y_pos   = 0
        width   = self._desktop_dimensions["width"] / 2
        height  = self._desktop_dimensions["height"]
        
        return self._generate_wmctrl_command_line(x_pos, y_pos, width, height)
    
    def create_move_to_window_west_command(self):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = 0
        y_pos   = 0
        width   = self._desktop_dimensions["width"] / 2
        height  = self._desktop_dimensions["height"]
        
        return self._generate_wmctrl_command_line(x_pos, y_pos, width, height)
    
    
    def _get_desktop_dimensions(self):
        """ get the desktop dimensions """
        command = "xdpyinfo | grep dimension"
        
        retval, output = self.execute_command(command)
        
        if retval == 1:
            raise Exception("Error: Cannot get the desktop dimensions. Err= %s" %(output['stderr']))
        
        stdout = ''.join(output['stdout'])
        
        #strToParse = "  dimensions:    1920x1200 pixels (650x406 millimeters)"
    
        pattern ="\s*dimensions:\s*(?P<width>\d*)x(?P<height>\d*)\spixels\s*"
        
        reSpec = re.compile(pattern, re.IGNORECASE)
    
        m = reSpec.match(stdout)
    
        if m is not None:
            self._desktop_dimensions = {"width" : int(m.group('width')), "height" : int(m.group('height'))}
            
        else:
            raise Exception("Error: Cannot find dimensions in %s" % (stdout))
        
            
    def execute_command(self, a_command, a_timeout = 10800):
        """ send active windows to north east corner """
        #information returned to the user
        user_info = { 'stdout' : [], 'stderr' : []}
        
        #execute process 
        proc = subprocess.Popen(a_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env= self._get_env())
        
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
                    user_info['stdout'].append(buf)
                    #nothing else to read => stdout is closed and the processed is finished
                    if not buf:
                        proc.stdout.close()
                        reading_on_stdout = False
                        inputs.remove(proc.stdout)
                        
                elif src_fd == proc.stderr:
                    buf = src_fd.read(self._buffer_size)
                    user_info['stderr'].append(buf)
                    #nothing else to read => stdout is closed and the processed is finished
                    if not buf:
                        proc.stderr.close()
                        reading_on_stderr = False
                        inputs.remove(proc.stderr)

        # for the moment wait for ever (will have find a way to kill the process if necessary)
        retval = proc.wait()
        
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
        #return the_env
        return os.environ
        



if __name__ == '__main__':
    
    
    helper = WMCTRLHelper(50*1024, 10000,"/homespace/gaubert/bin/wmctrl")
    
    helper._get_desktop_dimensions()
    
    retval, user_info = helper.execute_command(helper.create_move_to_window_north_east_command())
    
    time.sleep(1)
    
    retval, user_info = helper.execute_command(helper.create_move_to_window_north_west_command())
    
    time.sleep(1)
    
    retval, user_info = helper.execute_command(helper.create_move_to_full_screen_command())
    
    
    #print("retval, userinfo = %s, %s\n" % (retval, user_info))