'''
Created on Sep 16, 2009

@author: aubert
'''

# unit tests part
import unittest
import sys
import os
import org.ctbto.conf.conf_tests
from org.ctbto.conf.conf_helper import Conf




def tests():
    suite = unittest.TestLoader().loadTestsFromModule(org.ctbto.conf.conf_tests)
    unittest.TextTestRunner(verbosity=2).run(suite)


class TestConf(unittest.TestCase):
    
    def _get_tests_dir_path(self):
        """ get the org.ctbto.conf.tests path depending on where it is defined """
        
        fmod_path = org.ctbto.conf.__path__
        
        test_dir = "%s/tests"%fmod_path[0]
        
        return test_dir
    
    def setUp(self):
         
        # necessary for the include with the VAR ENV substitution
        os.environ["DIRCONFENV"] = self._get_tests_dir_path()
         
        self.conf = Conf(use_resource=False)
    
        fp = open('%s/%s' % (self._get_tests_dir_path(), "test.config"))
    
        self.conf._read(fp,"the file") #IGNORE:W0212
        
    def test_print_module_path(self):
        
        print("org.ctbto.conf module is loaded from %s\n" % (self._get_tests_dir_path()))
    
    def test_get_objects(self):
        """testGetObjects: test getter from all types """
        # get simple string
        astring = self.conf.get("GroupTest1", "astring")
        
        self.assertEqual(astring,"oracle.jdbc.driver.OracleDriver")
        
        # get an int
        aint = self.conf.getint("GroupTest1", "aint")
        
        self.assertEqual(aint,10)
        
        # get floatcompile the statements
        afloat = self.conf.getfloat("GroupTest1", "afloat")
        
        self.assertEqual(afloat,5.24)
        
        # get different booleans form
        abool1 = self.conf.getboolean("GroupTest1", "abool1")
        
        self.assertEqual(abool1, True)
        
        abool2 = self.conf.getboolean("GroupTest1", "abool2")
        
        self.assertEqual(abool2, False)
        
        abool3 = self.conf.getboolean("GroupTest1", "abool3")
        
        self.assertEqual(abool3, True)
        
        abool4 = self.conf.getboolean("GroupTest1", "abool4")
        
        self.assertEqual(abool4 ,False)
        
    def test_get_defaults(self):
        """testGetDefaults: test defaults values """
        
        # get all defaults
        astring = self.conf.get("GroupTest","astring","astring")
        
        self.assertEqual(astring,"astring")
        
        # get an default for int
        aint = self.conf.getint("GroupTest","aint",2)
        
        self.assertEqual(aint,2)
        
        # get float
        afloat = self.conf.getfloat("GroupTest","afloat",10.541)
        
        self.assertEqual(afloat,10.541)
        
        abool1 = self.conf.getboolean("GroupTest","abool1",True)
        
        self.assertEqual(abool1,True)
        
        abool2 = self.conf.getboolean("GroupTest","abool2",False)
        
        self.assertEqual(abool2,False)
        
        # existing group no option
        abool5 = self.conf.getboolean("GroupTest1","abool32",False)
        
        self.assertEqual(abool5,False)
        
    def test_var_substitutions(self):
        """testVarSubstitutions: test variables substitutions"""
        
        # simple substitution
        apath = self.conf.get("GroupTestVars","path")
        
        self.assertEqual(apath,"/foo/bar//tmp/foo/bar/bar/foo")
        
        # multiple substitution
        apath = self.conf.get("GroupTestVars","path1")
        
        self.assertEqual(apath,"/foo//tmp/foo/bar//foo/bar//tmp/foo/bar/bar/foo/bar")
        
        # nested substitution
        nested = self.conf.get("GroupTestVars","nested")
        
        self.assertEqual(nested,"this is done")  
        
    def test_include(self):
        """testInclude: test includes """
        val = self.conf.get("IncludedGroup","hello")
        
        self.assertEqual(val,'foo')
        
    def _create_fake_conf_file_in_tmp(self):
        
        f = open('/tmp/fake_conf.config','w')
        
        f.write('\n[MainDatabaseAccess]\n')
        f.write('driverClassName=oracle.jdbc.driver.OracleDriver')
        f.flush()
        f.close()
    
    def test_use_conf_ENVNAME_resource(self):
        """testUseConfENVNAMEResource: Use default resource ENVNAME to locate conf file"""
        self._create_fake_conf_file_in_tmp()
        
        # need to setup the ENV containing the the path to the conf file:
        os.environ[Conf.ENVNAME] = "/tmp/fake_conf.config"
   
        self.conf = Conf.get_instance()
        
        s = self.conf.get("MainDatabaseAccess","driverClassName")
        
        self.assertEqual(s,'oracle.jdbc.driver.OracleDriver')
    
    def test_read_from_CLI(self):
        """testReadFromCLI: do substitutions from command line resources"""
        #set environment
        os.environ["TESTENV"] = "/tmp/foo/foo.bar"
        
        val = self.conf.get("GroupTest1","fromenv")
   
        self.assertEqual(val,'/mydir//tmp/foo/foo.bar')
        
        #set cli arg
        sys.argv.append("--LongName")
        sys.argv.append("My Cli Value")
        
        val = self.conf.get("GroupTest1","fromcli1")
   
        self.assertEqual(val,'My Cli Value is embedded')
        
        #check with a more natural cli value
        val = self.conf.get("GroupTest1","fromcli2")
   
        self.assertEqual(val,'My Cli Value is embedded 2')
    
    def test_read_from_ENV(self):
        """testReadFromENV: do substitutions from ENV resources"""
        #set environment
        os.environ["TESTENV"] = "/tmp/foo/foo.bar"
        
        val = self.conf.get("ENV","TESTENV")
        
        self.assertEqual(val,"/tmp/foo/foo.bar")
        
        #set cli arg
        sys.argv.append("--LongName")
        sys.argv.append("My Cli Value")
        
        val = self.conf.get("CLI","LongName")
        
        self.assertEqual(val,"My Cli Value")
        
        # get a float from env
        os.environ["TESTENV"] = "1.05"
        
        val = self.conf.getfloat("ENV","TESTENV")
        
        self.assertEqual(val+1,2.05) 
    
    def test_print_content(self):
        """ test print content """
        
        #set environment
        os.environ["TESTENV"] = "/tmp/foo/foo.bar"
        
        #set cli arg
        sys.argv.append("--LongName")
        sys.argv.append("My Cli Value")
        
        substitute_values = True
        
        result = self.conf.print_content( substitute_values )
        
        self.assertNotEqual(result, '')
        
    def test_value_as_List(self):
        """ Value as List """
        
        the_list = self.conf.getlist('GroupTestValueStruct','list')
        
        self.assertEqual(the_list,['a', 1, 3])
    
    def test_value_as_dict(self):
        """Dict as Value """
        
        the_dict = self.conf.get_dict('GroupTestValueStruct','dict')
        
        self.assertEqual(the_dict, {'a': 2, 'b': 3})
    
    def test_complex_dict(self):
        """ complex dict """
        the_dict = self.conf.get_dict('GroupTestValueStruct','complex_dict')
        
        self.assertEqual(the_dict, {'a': 2, 'c': {'a': 1, 'c': [1, 2, 3], 'b': [1, 2, 3, 4, 5, 6, 7]}, 'b': 3})
    
    def test_dict_error(self):
        """ error with a dict """
        
        try:
            self.conf.get_dict('GroupTestValueStruct','dict_error')
        except Exception, err:
            self.assertEquals(err.message, "Expression \"{1:2,'v b': a\" cannot be converted as a dict.")
            return
        
        self.fail('Should never reach that point')
            
    def test_list_error(self):
        """ error with a list """
        
        try:
            the_list = self.conf.get_list('GroupTestValueStruct','list_error')
            print('the_list = %s\n' %(the_list))
        except Exception, err:
            self.assertEquals(err.message, 'Unsupported token (type: @, value : OP) (line=1,col=3).')
            return
         
        self.fail('Should never reach that point')
    
    def test_read_simple_values_from_par(self):
        """ test_read_simple_values_from_par: read simple values from a par file """
        
        #get from RNPAR group
        user = self.conf.get('RNPAR','rms_user')
        
        self.assertEquals(user,'rmsauto')
        
        #get from another group that references this one
        user1 = self.conf.get('GroupPARFileTest','rnuser')
        self.assertEquals(user1,'rmsauto')
    
    def test_includes_in_par(self):
        """ test get values from an include in a par file """
        
        #get from RNPAR group
        user = self.conf.get('RNPAR','another_user')
        
        self.assertEquals(user,'the_root_password')
        
        # test overloading
        overloading = self.conf.get('RNPAR','overloading')
        
        self.assertEquals(overloading,'overloaded')
    
    def test_variables_in_par(self):
        """ test that the variables are working in a par file """
        
        #reference a variable from another file
        value = self.conf.getint('RNPAR','value')
        
        self.assertEquals(value,42)
        
        val2 = self.conf.get('RNPAR','val2')
        
        self.assertEquals(val2,'/root/my_path/val/root1')
        
if __name__ == '__main__':
    tests()