'''
Created on Nov 8, 2011

@author: guillaume.aubert@eumetcast.int
'''

import unittest
import eumetsat.dmon.gems_feeder as gems_feeder

class TestGEMSFeeder(unittest.TestCase):

    def __init__(self, stuff):
        """ constructor """
        super(TestGEMSFeeder, self).__init__(stuff)
    
    def setUp(self):
        pass
    
    def test_get_facilities(self):
        """
           Get facilities
        """
        facilities = gems_feeder.GEMSExtractor.get_all_GEMS_facilities()
        
        self.assertEquals(facilities[0], 'COMMS')
        self.assertEquals(len(facilities), 97)
    
    def ztest_search(self):
        """
           test the search keywords
        """
        gems_extractor = gems_feeder.GEMSExtractor(start_time = "2011-11-05 00:00:00", end_time = "2011-11-07 00:00:00", severity = ["A","W","I"], facility = ['DVB_EUR_UPLINK'], search ='tc-send')
    
        lines = []
        cpt = 0
        for line in gems_extractor:
            if cpt < 3:
                lines.append(line)
            else:
                break
            cpt += 1
    
        self.assertEquals(lines[0]['msg'], 'send.log: Entry detected: MSG:2011-11-05 08:30:00.015:tc-send shutting down... [8160]')
     

    def ztest_simple_dates(self):
        """
           test gems extractor with simple dates
        """
        gems_extractor = gems_feeder.GEMSExtractor(start_time = "2011-11-05 00:00:00", end_time = "2011-11-07 00:00:00", severity = ["A","W","I"], facility = ['DVB_EUR_UPLINK'])
    
        lines = []
        cpt = 0
        for line in gems_extractor:
            if cpt < 3:
                lines.append(line)
            else:
                break
            cpt += 1
    
        self.assertEquals(lines[0]['msg'], 'xferlog: Entry detected: Sat Nov 5 00:00:01 2011 0 10.60.200.21 150156 /home/eumetsat/data/groups/EPS-NOAA-MHS-L1/mhs_20111104_220351_noaa19_14123_eps_o.l1_bufr.tmp b _ i r eumetsat ftp 0 * c')
     
    def ztest_get_3_lines(self):
        """
           create a gems extractor
        """
        gems_extractor = gems_feeder.GEMSExtractor(start_time = "11.308.15.02.03", end_time = "11.308.15.12.03", severity = ["A","W","I"], facility = ['DVB_EUR_UPLINK'])
    
        cpt = 0
        
        lines = []
        
        for line in gems_extractor:
            if cpt < 3:
                lines.append(line)
            else:
                #quit loop after 3 iters
                break
                
            cpt += 1
        
        self.assertEquals({'facility': u'DVB_EUR_UPLINK', \
                           'time': u'11.308.15.02.18.149', \
                           'agent': u'LogFileAgent', \
                           'host': u'eumet01.localdomain', \
                           'msg': u'xferlog: Entry detected: Fri Nov 4 15:01:18 2011 0 10.60.200.21 200429 /home/eumetsat/data/groups/EPS-METOP-ASCA-L1/ASCA_SZO_1B_M02_20111104135702Z_20111104135959Z_N_O_20111104150024Z.tmp b _ i r eumetsat ftp 0 * c',\
                           'lvl': u'I'}, \
                           lines[0], "First lines is not equal to what it should") 
        
        self.assertEquals(lines[2]['time'], '11.308.15.02.18.149') 
        
        self.assertEqual("A", "A","A is not equal to A")
        
        self.assertEquals(lines[2]['msg'], 'xferlog: Entry detected: Fri Nov 4 15:01:19 2011 3 137.129.9.61 369124 /home/eumetsat/data/retim/groups/retim-1567/HAJX81_ARPM_041200.20111104150058_P1567PTD6CF_REUFMFI.369124.GB.tmp b _ i r retim ftp 0 * c')
    
    def ztest_get_all_tcsend_restart_4_3_defined_days(self):
        """
           Get all the tc-send restart for the last 3 days
        """
        
        pass
        
        gems_extractor = gems_feeder.GEMSExtractor(start_time = "11.308.15.02.03", end_time = "11.308.15.12.03", severity = ["A","W","I"], facility = ['DVB_EUR_UPLINK'])
    
    

def tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGEMSFeeder)
    unittest.TextTestRunner(verbosity=2).run(suite)
 
if __name__ == '__main__':
    
    tests()