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
        
        
    def _generate_wmctrl_command_line(self, win_id, x, y, width, height):
        """
          wmctlr -r :ACTIVE: -e 1,x,y,width,height. for active window
          example "/bin/wmctrl -r :ACTIVE: -e 1,960,580,950,580"
        """
        
        return "%s -r %s -e 1,%s,%s,%s,%s" % (self._command, win_id, x, y, width, height)
        
    def create_move_to_full_screen_command(self, win_id, x_deco, y_deco):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = 0
        y_pos   = 0
        width   = self._desktop_dimensions["width"]  - x_deco
        height  = self._desktop_dimensions["height"] - y_deco
        
        return self._generate_wmctrl_command_line(win_id, x_pos, y_pos, width, height)
            
    def create_move_to_window_north_east_command(self, win_id, x_deco, y_deco, x_visible, y_visible ):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
           
           here is the formula with the decorations:
           x=(desktop width/2)
           y=0
           width  = (desktop width:1920/2) - x_deco = 960 - 8 = 952
           height = (desktop_height:1200) - y_deco = 1200 -32 = 1128


        
        """
        x_pos   = self._desktop_dimensions["width"] / 2
        y_pos   = 0
        width   = (self._desktop_dimensions["width"] / 2)  - (x_deco + x_visible)
        height  = (self._desktop_dimensions["height"] / 2) - (y_deco + y_visible)
        
        return self._generate_wmctrl_command_line(win_id, x_pos, y_pos, width, height)
    
    def create_move_to_window_north_west_command(self, win_id, x_deco, y_deco, x_visible, y_visible ):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
           here is the formula with the decorations:
           x=(desktop width/2)
           y=0
           width  = (desktop width:1920/2) - (x_deco+x_visible) = 960 - 8 = 952
           height = (desktop_height:1200) - (y_deco+y_visible)  = 1200 -32 = 1128
           
           with x_visible and y_visible the always visible parts like the kicker in kde
        
        """
        x_pos   = 0
        y_pos   = 0
        width   = self._desktop_dimensions["width"] / 2  - (x_deco + x_visible)
        height  = self._desktop_dimensions["height"] / 2 - (y_deco + y_visible)
        
        return self._generate_wmctrl_command_line(win_id, x_pos, y_pos, width, height)
    
    def create_move_to_window_east_command(self, win_id, x_deco, y_deco):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = self._desktop_dimensions["width"] / 2
        y_pos   = 0
        width   = (self._desktop_dimensions["width"] / 2) - x_deco
        height  = (self._desktop_dimensions["height"]) - y_deco
        
        return self._generate_wmctrl_command_line(win_id, x_pos, y_pos, width, height)
    
    def create_move_to_window_west_command(self, win_id, x_deco, y_deco):
        """ 
           Move command north_east.
           -e gravity,x_position,y_position,width,height
        
        """
        x_pos   = 0
        y_pos   = 0
        width   = (self._desktop_dimensions["width"] / 2) - x_deco
        height  = self._desktop_dimensions["height"] - y_deco
        
        return self._generate_wmctrl_command_line(win_id, x_pos, y_pos, width, height)
    
    def _get_active_window_command(self):
        """
          get the active window id
        """
        command = "xprop -root | grep '_NET_ACTIVE_WINDOW(WINDOW)' | awk '{print $5}'"
        
        retval, output = self.execute_command(command)
        
        if retval == 1:
            raise Exception("Error: Cannot get the active window")
        
        id = ''.join(output['stdout'])
        
        return id.strip()
    
    def _get_window_decoration_dimensions(self, a_win_id):
        """ 
           get the window decoration dimensions
           call border.sh id
        """
        
        command = "./border.sh %s" % (a_win_id)
        
        retval, output = self.execute_command(command)
        
        if retval == 1:
            raise Exception("Error: Cannot get the border dimensions")
        
        stdout = ''.join(output['stdout'])
        
        pattern = "\s*Class=\"\w*\",\s*Name=\"\w*\",\s*N=(?P<N>\d*)\s*,\s*E=(?P<E>\d*)\s*,\s*S=(?P<S>\d*)\s*,\s*W=(?P<W>\d*)\s*"
        
        re_decorations = re.compile(pattern, re.IGNORECASE)
        
        match = re_decorations.match(stdout)
        
        decoration_dimensions = { 'N' : -1 , 'S' : -1, 'W' : -1, 'E' : -1 , 'Y' : -1, 'X' : -1}
        
        if match is not None:
            decoration_dimensions = { 'N' : int(match.group('N')) , \
                                      'S' : int(match.group('S')), \
                                      'W' : int(match.group('W')), \
                                      'E' : int(match.group('E'))
                                    }
            
            decoration_dimensions['Y'] = decoration_dimensions['N'] + decoration_dimensions['S']
            decoration_dimensions['X'] = decoration_dimensions['W'] + decoration_dimensions['E']
            
        return decoration_dimensions
        
    
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
    
    active_window_id = helper._get_active_window_command()
    
    print("active_window_id = %s\n" %(active_window_id))
    
    decorations_dim = helper._get_window_decoration_dimensions(active_window_id)
    
    print("add y=%d, x=%d\n" % ( decorations_dim['Y'],decorations_dim['X']) )
    
    retval, user_info = helper.execute_command(helper.create_move_to_window_north_east_command(active_window_id, decorations_dim['X'], decorations_dim['Y'],0,40))
    
    #time.sleep(1)
    
    #retval, user_info = helper.execute_command(helper.create_move_to_window_north_west_command())
    
    #time.sleep(1)
    
    #retval, user_info = helper.execute_command(helper.create_move_to_full_screen_command())
    
    
    #print("retval, userinfo = %s, %s\n" % (retval, user_info))