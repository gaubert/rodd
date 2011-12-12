'''
Created on Nov 29, 2011

@author: guillaume.aubert@eumetsat.int
'''
import os
import curses
import datetime
import time

import eumetsat.dmon.common.time_utils as time_utils
import eumetsat.dmon.common.log_utils  as log_utils
import eumetsat.dmon.common.analyze_utils as analyze_utils

class CurseDisplay(object):
    '''
       A simple Curse display
    '''
    LOG = log_utils.LoggerFactory.get_logger('CurseDisplay')
    
    def __init__(self):
        """
           constructor
        """
        self._full_screen = curses.initscr()
        
        #get screen size
        self._maxy, self._maxx = self._full_screen.getmaxyx()
        
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        #curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLUE)
        self._full_screen.keypad(1)
        
        self._full_screen.bkgd(curses.color_pair(1))
        self._full_screen.box()
        self._full_screen.refresh()
        # to have non blocking getch
        self._full_screen.nodelay(1)
          
        self._total_pad    = curses.newpad(100,300)
        self._active_pad   = curses.newpad(500, 500)
        self._finished_pad = curses.newpad(500, 500)
        
        #used to colorized elems that have changed since last update on screen
        self._previous_display_time = None
        
        self._previous_snapshot = {}
        
        
    def check_for_input(self):
        """
           Check for inputs
        """  
        char = self._full_screen.getch()
        if char in [ord('x'), ord('q')]:
            #QUIT
            return "QUIT"
        elif char in [ord('s')]:
            return "STOPACCEPTING"
        elif char in [ord('r')]:
            return "RESTARTACCEPTING"
    
    def print_screen(self, a_db, a_current_display_time):
        """
           print on screen
        """
        
        #constants to be put in files
        nb_max_active_records   = 70
        nb_max_finished_records = 30
        
        # get min max screen size
        self._maxy, self._maxx = self._full_screen.getmaxyx()
        
        total_pad    = curses.newpad(100,300)
        active_pad   = curses.newpad(500, 500)
        finished_pad = curses.newpad(500, 500)
        
        header_active   = "-ACTIVE-----------------------------------------------------------------------------------------------------------------------------------------------------------"
        header_finished = "-FINISHED---------------------------------------------------------------------------------------------------------------------------------------------------------"
        header          = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |       sent      |"
        
        template = "%s|%s|%s|%s|%s|%s|%s|"
        
        active_pad.addstr(1, 1, header_active)
        active_pad.addstr(2, 1, header)
        active_printed_records = 0
        
        finished_pad.addstr(1, 1, header_finished)
        finished_pad.addstr(2, 1, header)
        finished_printed_records = 0
        
        #set x 
        x_active   = 3
        x_finished = 3
                      
        CurseDisplay.LOG.info("------ start Printing on screen ------")
        
        #reverse iteration from the lastest records to the oldest one
        for index in a_db._last_update.get_sorted_iter(sorted, reverse = True):
            
            # if index which is the last_update_time is superior to the previous_display_time
            # meaning was updated since the last display then change color
            if not self._previous_display_time or (index > self._previous_display_time):
                color = curses.A_BOLD
            else:
                color = curses.color_pair(0)
            
            for record in a_db._last_update[index]:
             
                rec = record
                
                #CurseDisplay.LOG.info('fn=%s, jn=%s, cr=%s, up=%s,an=%s,bl=%s,lupdate=%s' % ( rec['filename'], rec['jobname'], \
                #                                                                            time_utils.datetime_to_time(rec['created']), time_utils.datetime_to_time(rec['uplinked']), \
                #                                                                            time_utils.datetime_to_time(rec['announced']), time_utils.datetime_to_time(rec['blocked']), \
                #                                                                            time_utils.datetime_to_time(rec['last_update'])) )
                #reduce filename and jobname size to 50
                filename = record['filename']
                if filename:
                    filename = os.path.basename(filename)
                    
                    #will not fail if name < 50
                    filename = filename[:50]
                else:
                    filename = "-"
                
                jobname = record['jobname']
                if jobname:
                    #will not fail if name < 20
                    jobelems = jobname.split('-')
                    jobname  = "%s..-%s" % (jobname[:13], jobelems[-1])
                else:
                    jobname = "-"
                
                uplinked = record.get('uplinked', None)
                if not uplinked:
                    uplinked = "-"
                else:
                    uplinked = time_utils.datetime_to_compactdate(uplinked)
                    
                queued   = record.get('queued', None)
                if not queued:
                    queued = "-"
                else:
                    queued = time_utils.datetime_to_compactdate(queued)
                
                annouc   = record.get('announced', None)
                if not annouc:
                    annouc = "-"
                else:
                    annouc = time_utils.datetime_to_compactdate(annouc)
                    
                blocked   = record.get('blocked', None)
                if not blocked:
                    blocked = "-"
                else:
                    blocked = time_utils.datetime_to_compactdate(blocked)
                    
                finished = record.get('finished', None)
                #active
                if not finished:
                    finished = "-"        
                else:
                    finished = time_utils.datetime_to_compactdate(finished)
                
                str_to_print = template % (filename.ljust(50) if filename != '-' else filename.center(50), \
                                uplinked.center(17),\
                              queued.center(17),jobname.center(20), \
                              blocked.center(17),  annouc.center(17),\
                              finished.center(17))
                
                #add records to be printed in the right area
                #it means this is active    
                if finished == "-":
                    if active_printed_records < nb_max_active_records:
                        #insert record to be printed
                        active_pad.addstr(x_active, 1, str_to_print, color)
                        x_active += 1
                        active_printed_records += 1
                else:
                    #finished
                    if finished_printed_records < nb_max_finished_records:
                        #insert record to be printed
                        finished_pad.addstr(x_finished, 1, str_to_print, color )
                        x_finished += 1
                        finished_printed_records += 1
            
            
        
        #active pad take 2/3 of the space available
        # noutrefresh(a, b, minrow, mincol, maxrow, maxcol) with a and b the starting point in the pad
        # with the 4 coordinates the position in the full screen
        
        results = analyze_utils.get_active_jobs(a_db, self._previous_snapshot)
        self._previous_snapshot = results['since_last_print']['prev_snapshot']
        
        first_line = "Active transfers: %s Blocked transfers : %s Active jobs: %s Total nb entries: %s Finished entries in db: %s " % (str(results['active_file_transfers']).ljust(3), \
                                                                                        str(results['blocked_file_transfers']).ljust(3), str(results['nb_jobs']).ljust(3), \
                                                                                        str(results['total_nb_of_transfers']).ljust(3), str(results['finished_file_transfers']).ljust(3))
        
        sec_line   = "New entries     : %s Finished transfers: %s Cleaned entries   : %s [Since last refresh (2s)]" % (str(results['since_last_print']['deleted']).ljust(3), \
                                                                                             str(results['since_last_print']['new']).ljust(3), \
                                                                                             str(results['since_last_print']['finished']).ljust(3))
        
        total_pad.addstr(1, 1, first_line , curses.A_BOLD)
        
        total_pad.addstr(2, 1, sec_line, curses.A_BOLD)
        
        total_pad.addstr(3, 1,"")
        
        total_pad.noutrefresh(1, 1, 1, 1, 2, self._maxx-2)
        
        active_pad.noutrefresh(1, 1, 4, 1, int(round(self._maxy-2)*(2.00/3))+1, self._maxx-2)
        
        finished_pad.noutrefresh(1, 1, int(round((self._maxy-2)*(2.00/3)))+2, 1, self._maxy-2, self._maxx-2)
        
        
        curses.doupdate()
        
        #update previous_display_time with the current display time
        self._previous_display_time = a_current_display_time
        
        #time.sleep(1)
    
    def reset_screen(self):
        """
           Clean screen
        """
        curses.nocbreak()
        self._full_screen.keypad(0)
        curses.echo()
        curses.endwin()


class TextDisplay(object):
    '''
       A simple text display
    '''
    LOG = log_utils.LoggerFactory.get_logger('TextDisplay')
    
    def __init__(self):
        """
           constructor
        """
        pass
    
    def check_for_input(self):
        """
           Check for inputs
        """  
        return None

    def print_screen(self, a_db, a_current_time):
        """
          print a table
        """
        header_Active   = "--Active----------------------------------------------------------------------------------------------------------------------------------------------------------\n"
        header_Finished = "--Finished--------------------------------------------------------------------------------------------------------------------------------------------------------\n"
        
        header          = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |     finished    |\n"
        
        template = "%s|%s|%s|%s|%s|%s|%s|\n"
        
        active_data = header_Active   + header
        finish_data = header_Finished + header
        
        #reverse iteration from the lastest records to the oldest one
        for index in a_db._last_update.get_sorted_iter(sorted, reverse = True):
            
            record_list = a_db._last_update[index]
            
            for record in record_list:
                #reduce filename and jobname size to 50
                filename = record['filename']
                if filename:
                    filename = os.path.basename(filename)
                    
                    #will not fail if name < 50
                    filename = filename[:50]
                else:
                    filename = "-"
                
                jobname = record['jobname']
                if jobname:
                    #will not fail if name < 20
                    jobelems = jobname.split('-')
                    jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
                else:
                    jobname = "-"
                
                uplinked = record.get('uplinked', None)
                if not uplinked:
                    uplinked = "-"
                else:
                    uplinked = time_utils.datetime_to_compactdate(uplinked)
                    
                queued   = record.get('queued', None)
                if not queued:
                    queued = "-"
                else:
                    queued = time_utils.datetime_to_compactdate(queued)
                
                annouc   = record.get('announced', None)
                if not annouc:
                    annouc = "-"
                else:
                    annouc = time_utils.datetime_to_compactdate(annouc)
                    
                blocked   = record.get('blocked', None)
                if not blocked:
                    blocked = "-"
                else:
                    blocked = time_utils.datetime_to_compactdate(blocked)
                    
                finished = record.get('finished', None)
                if not finished:
                    finished = "-"
                else:
                    finished = time_utils.datetime_to_compactdate(finished)
                    
                if finished == '-':
                    active_data += template % (filename.ljust(50) if filename != '-' else filename.center(50), uplinked.center(17),\
                                  queued.center(17),jobname.center(20), \
                                  blocked.center(17),  annouc.center(17),\
                                  finished.center(17))
                else:
                    finish_data += template % (filename.ljust(50) if filename != '-' else filename.center(50), uplinked.center(17),\
                                  queued.center(17),jobname.center(20), \
                                  blocked.center(17),  annouc.center(17),\
                                  finished.center(17))
            
           
        print("%s\n%s" %(active_data, finish_data) )
        
        
    
    def reset_screen(self):
        """
           Do nothing
        """
        pass
    
    

    def old_print_table(self, a_db):
        """
          print a table
        """
        header_l = "------------------------------------------------------------------------------------------------------------------------------------------------------------------"
        header   = "                   filename                       |    uplinked     |      queued     |       jobname      |    blocked      |    announced    |     finished    |"
        template = "%s|%s|%s|%s|%s|%s|%s|"
        
        print(header)
        
        for record in a_db:
            
            #reduce filename and jobname size to 50
            filename = record['filename']
            if filename:
                filename = os.path.basename(filename)
                
                #will not fail if name < 50
                filename = filename[:50]
            else:
                filename = "-"
            
            jobname = record['jobname']
            if jobname:
                #will not fail if name < 20
                jobelems = jobname.split('-')
                jobname  = "%s..-%s" %(jobname[:13],jobelems[-1])
            else:
                jobname = "-"
            
            uplinked = record.get('uplinked', None)
            if not uplinked:
                uplinked = "-"
            else:
                uplinked = time_utils.datetime_to_compactdate(uplinked)
                
            queued   = record.get('queued', None)
            if not queued:
                queued = "-"
            else:
                queued = time_utils.datetime_to_compactdate(queued)
            
            annouc   = record.get('announced', None)
            if not annouc:
                annouc = "-"
            else:
                annouc = time_utils.datetime_to_compactdate(annouc)
                
            blocked   = record.get('blocked', None)
            if not blocked:
                blocked = "-"
            else:
                blocked = time_utils.datetime_to_compactdate(blocked)
                
            finished = record.get('finished', None)
            if not finished:
                finished = "-"
            else:
                finished = time_utils.datetime_to_compactdate(finished)
            
            print(template % (filename.ljust(50) if filename != '-' else filename.center(50), uplinked.center(17),\
                              queued.center(17),jobname.center(20), \
                              blocked.center(17),  annouc.center(17),\
                              finished.center(17)))
        
        print(header_l)