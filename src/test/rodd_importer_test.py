'''
Created on 25 Jun 2010

@author: guillaume.aubert@eumetsat.int
'''
import unittest
import eumetsat.rodd_extractor
import eumetsat.db.rodd_importer

class RoddImporterTest(unittest.TestCase):
    """ LexerTest """
    
    def setUp(self):
        """ setUp method """
        pass
      
    def test_print(self):
        print("\n*******This is a test\n")
        
    def test_simply(self):
        
        importer = eumetsat.db.rodd_importer.RoddImporter("'mysql://root@localhost/rodd'")


if __name__ == '__main__':
    print "Hello\n"
    #suite = unittest.TestSuite()
    #suite.addTest(RoddImporterTest('test_print'))
    #unittest.TextTestRunner(verbosity=2).run(suite)