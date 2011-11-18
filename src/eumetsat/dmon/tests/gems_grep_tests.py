'''
Created on Nov 8, 2011

@author: guillaume.aubert@eumetcast.int
'''
import sys
import unittest
import datetime

import eumetsat.dmon.gems_grep as gems_grep_mod
import eumetsat.dmon.common.time_utils as time_utils


class TestGEMSGrep(unittest.TestCase):

    def __init__(self, stuff):
        """ constructor """
        super(TestGEMSGrep, self).__init__(stuff)
    
    def setUp(self):
        pass
    
    def test_default_facilities(self):
        """
           test default facilities
        """
        sys.argv = ['/homespace/gaubert/ecli-workspace/rodd/src/eumetsat/dmon/gems_grep.py', \
                   ]
    
        gems_grep = gems_grep_mod.GEMSGrep()
    
        args = gems_grep.parse_args()
        
        facilities = gems_grep._process_facilities(args)
        
        self.assertEquals([u'COMMS'], facilities)
        
    def test_all_facilities(self):
        """
           test all facilities
        """
        sys.argv = ['/homespace/gaubert/ecli-workspace/rodd/src/eumetsat/dmon/gems_grep.py', \
                    '--facilities', 'ALL'
                   ]
    
        gems_grep = gems_grep_mod.GEMSGrep()
    
        args = gems_grep.parse_args()
        
        facilities = gems_grep._process_facilities(args)
        
        self.assertEquals('COMMS', facilities[0])
        self.assertEquals('MASIF-OPE-INT', facilities[42])
        self.assertEquals(len(facilities), 97)
        
    def test_fac_facilities(self):
        """
           test default facilities
        """
        sys.argv = ['/homespace/gaubert/ecli-workspace/rodd/src/eumetsat/dmon/gems_grep.py', \
                    '--facilities', 'COMMS, DVB_EUR_UPLINK'
                   ]
    
        gems_grep = gems_grep_mod.GEMSGrep()
    
        args = gems_grep.parse_args()
        
        facilities = gems_grep._process_facilities(args)
        
        self.assertEquals(['COMMS', 'DVB_EUR_UPLINK'], facilities)
    
    def test_valid_dates(self):
        """
           test valid dates
        """
       
        sys.argv = ['/homespace/gaubert/ecli-workspace/rodd/src/eumetsat/dmon/gems_grep.py', \
                    '--from', '2011-04-03T14:30:00', \
                    '--until', '2011-05-04T14:40:00', \
                    "dmon.log"]
    
        gems_grep = gems_grep_mod.GEMSGrep()
    
        args = gems_grep.parse_args()
    
        dfrom, duntil =  gems_grep._process_dates(args)
        
        self.assertEquals(dfrom, time_utils.convert_date_str_to_datetime("2011-04-03T14:30:00"))
        
        self.assertEquals(duntil, time_utils.convert_date_str_to_datetime("2011-05-04T14:40:00"))
        
    def test_from_anterior_to_until(self):
        """
           test valid dates
        """
        sys.argv = ['/homespace/gaubert/ecli-workspace/rodd/src/eumetsat/dmon/gems_grep.py', \
                    '--from', '2011-06-03T14:30:00', \
                    '--until', '2011-05-04T14:40:00', \
                    "dmon.log"]
    
        gems_grep = gems_grep_mod.GEMSGrep()
    
        args = gems_grep.parse_args()
    
        try:
            _, _  =  gems_grep._process_dates(args)
        except Exception, exce:
            self.assertEquals(exce.message, 'from date (2011-06-03T14:30:00) cannot be posterior to until date (2011-05-04T14:40:00)')
        
    def test_default_date(self):
        '''
           Test that the default dates are put
        '''
        # can check that there is one hour between from and until
        sys.argv = ['/homespace/gaubert/ecli-workspace/rodd/src/eumetsat/dmon/gems_grep.py', \
                   ]
        
        gems_grep = gems_grep_mod.GEMSGrep()
    
        args = gems_grep.parse_args()
        
        dfrom, duntil =  gems_grep._process_dates(args)
        
        self.assertEqual( (duntil- dfrom), datetime.timedelta(hours=1))
        
        

def tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGEMSGrep)
    unittest.TextTestRunner(verbosity=2).run(suite)
 
if __name__ == '__main__':
    
    tests()