'''
Created on Nov 29, 2011

@author: guillaume.aubert@eumetsat.int
'''
import os
import curses

import eumetsat.dmon.common.time_utils as time_utils
import eumetsat.dmon.common.log_utils  as log_utils

def get_active_jobs(database):
    """
       Get the number of active jobs
    """
    finished_nb = 0
    blocked     = 0
    
    for rec in database:
        if rec.get('finished_time_insert', None):
            finished_nb += 1
        
        if rec.get('blocked', None):
            blocked +=1
    
    return len(database)-finished_nb, finished_nb, blocked

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
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLUE)
        self._full_screen.keypad(1)
        
        self._full_screen.bkgd(curses.color_pair(1))
        self._full_screen.box()
        self._full_screen.refresh()
        # to have non blocking getch
        self._full_screen.nodelay(1)
         
        CurseDisplay.LOG.debug("maxy = %d, maxx = %d\n" %(self._maxy, self._maxx))
        
        self._active_pad   = curses.newpad(1000, 1000)
        self._finished_pad = curses.newpad(1000, 1000)
        
        
    def check_for_input(self):
        """
           Check for inputs
        """  
        char = self._full_screen.getch()
        if char in [ord('x'), ord('q')]:
            #QUIT
            return "QUIT"
        else:
            return None
        
    def print_index(self, a_db):
        """
        """
        
        for rec in a_db._last_update.get_sorted_iter(sorted, reverse = True):
            CurseDisplay.LOG.info("sorted rec = %s" %(rec))
    
    def print_screen(self, a_db):
        """
           print on screen
        """
        #constants to be put in files
        nb_max_active_records   = 70
        nb_max_finished_records = 30
        
        active_pad   = self._active_pad
        finished_pad = self._finished_pad
        
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
        
        active, finished, blocked = get_active_jobs(a_db)
                
        CurseDisplay.LOG.info("active jobs = %d, finished jobs=%d, blocked=%d" % (active, finished, blocked) )
        
        CurseDisplay.LOG.info("------ start Printing on screen ------")
        
        #reverse iteration from the lastest records to the oldest one
        for index in a_db._last_update.get_sorted_iter(sorted, reverse = True):
            
            for record in a_db._last_update[index]:
             
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
                        active_pad.addstr(x_active, 1, str_to_print )
                        x_active += 1
                        active_printed_records += 1
                else:
                    #finished
                    if finished_printed_records < nb_max_finished_records:
                        #insert record to be printed
                        finished_pad.addstr(x_finished, 1, str_to_print )
                        x_finished += 1
                        finished_printed_records += 1
            
            
        finished_pad.noutrefresh(1, 1, int(round((self._maxy-2)*(2.00/3)))+1 , 1, self._maxy-2, self._maxx-2)
        active_pad.noutrefresh(1, 1, 1, 1, int(round(self._maxy-2)*(2.00/3)) , self._maxx-2)
        
        curses.doupdate()
    
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

    def print_screen(self, a_db):
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