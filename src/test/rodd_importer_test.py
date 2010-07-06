'''
Created on 25 Jun 2010

@author: guillaume.aubert@eumetsat.int
'''
import unittest

import eumetsat.rodd_extractor
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
      
    def test_print(self):
        pass
        
    def test_simply(self):
        " Very simple test"
        importer = eumetsat.db.rodd_importer.RoddImporter("mysql://root@127.0.0.1/rodd")


if __name__ == '__main__':
    
    tests()