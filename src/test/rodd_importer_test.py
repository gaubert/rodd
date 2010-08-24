'''
Created on 25 Jun 2010

@author: guillaume.aubert@eumetsat.int
'''
import unittest

import eumetsat.readers.xml_rodd_extractor
import eumetsat.readers.csv_light_rodd_extractor as csv_extractor
import eumetsat.db.rodd_importer

def tests():
    
    # load all the test from a class
    suite = unittest.TestLoader().loadTestsFromTestCase(RoddImporterTest)
    
    # load individual test
    #suite = unittest.TestLoader().loadTestsFromModule(test)
    #suite.addTest(RoddImporterTest('test_print'))
    
    
    unittest.TextTestRunner(verbosity=2).run(suite)

class RoddImporterTest(unittest.TestCase):
    """ LexerTest """
    
    def setUp(self):
        """ setUp method """
        pass
      
    def ztest_rodd_xml_extractor(self):
        ''' test rodd extractor '''
        
        extractor = eumetsat.readers.xml_rodd_extractor.RoddExtractor('/cygdrive/h/Dev/ecli-workspace/rodd/etc/data/rodd-data')
        extractor.read_xml()
    
    def test_rodd_csv_extractor(self):
        ''' test csv rodd extractor '''
        
        db_url   = "mysql://rodd:ddor@tclxs30/RODD"
        root_dir = "/homespace/gaubert/ecli-workspace/rodd/etc/data/rodd-data/csv"
        
        extractor = csv_extractor.LCSVRoddExtractor(root_dir, db_url)
        extractor.clean_table("RODD", "products")
        extractor.read_csv_and_insert_product_sql(csv_extractor.LCSVRoddExtractor.LIGHT_PRODUCT_TABLE_COLS)
        
    def ztest_rodd_importer(self):
        ''' test rodd importer '''
        importer = eumetsat.db.rodd_importer.RoddImporter("mysql://root@127.0.0.1/rodd")
        
        importer.import_table_products([])


if __name__ == '__main__':
    tests()