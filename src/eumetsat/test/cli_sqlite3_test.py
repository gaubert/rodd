'''
Created on Sep 22, 2010

@author: gaubert
'''

import unittest
import flask
import subprocess

import eumetsat.viewer.flask_server

DATA_DIR = "/homespace/gaubert/ecli-workspace/rodd/etc/test/data"

class RODDTestCase(unittest.TestCase):
    
    def _clean_db(self):
        """ clean the database """
        print("=> cleaning db")
        script = "/homespace/gaubert/ecli-workspace/rodd/etc/test/clean_sqlite3_db.sh"
        res = subprocess.call(script)
        self.assertEqual(res,0,"Could not clean properly the database when running %s" % (script))
        print("=== Db reseted. Start the tests")
        
    def test_get_add_delete_channel(self):
        """**********  add a add, get it and delete it **************"""
        
        OK_ADD_CHAN  = {'result': {'status': 'OK', 'messages': ['Added Channel AIDA-16.', 'Added Channel AIDA-17.', 'Added ServiceDir aida-2-test.', 'Added ServiceDir aida-3-test.', 'Added ServiceDir aida-4-test.']}} 
        OK_GET_CHAN  = {'channels': [{'min_rate': '400000', 'multicast_address': '224.223.222.223:4711', 'max_rate': '1', 'channel_function': 'AIDA-16', 'name': 'AIDA-16'}, {'min_rate': '400000', 'multicast_address': '224.223.222.223:4711', 'max_rate': '3', 'channel_function': 'AIDA-17', 'name': 'AIDA-17'}]} 
        OK_DEL_CHAN  = {'status': 'OK', 'messages': ['channel AIDA-16 deleted']} 
        OK_NO_CHAN   = {'channels': [{'min_rate': '400000', 'multicast_address': '224.223.222.223:4711', 'max_rate': '3', 'channel_function': 'AIDA-17', 'name': 'AIDA-17'}]} 
       
        print("\n")
       
        self._clean_db()
        
        the_file = open("%s/channels.json" % (DATA_DIR))
        json_text = the_file.read()
        
        #get client
        client = eumetsat.viewer.flask_server.app.test_client()
        
        #add product
        print("=> add channels \n")
        returned_val = client.post('/channels', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_ADD_CHAN, "Fail when adding channel. \n%s \nis different from \n%s" % (data, OK_ADD_CHAN))
        
        #get products
        print("=> get channels\n")
        returned_val = client.get("/channels", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_GET_CHAN, "Fail when getting channel. \n%s \nis different from \n%s" % (data, OK_ADD_CHAN))
        
        prod_id = 'AIDA-16'
        
        #delete product
        print("=> delete channels\n")
        returned_val = client.delete("/channels/%s" % (prod_id), content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        self.assertDictEqual(data, OK_DEL_CHAN, "Fail when deleting channel. \n%s \nis different from \n%s" % (data, OK_ADD_CHAN))
        
        # getting product one more time
        print("=> get channel\n")
        returned_val = client.get("/channels", content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        self.assertDictEqual(data, OK_NO_CHAN, "Fail when getting channel. \n%s \nis different from \n%s" % (data, OK_NO_CHAN))

    def test_get_add_delete_servdirs(self):
        """**********  add a servicedir, get it and delete it **************"""
        
        OK_ADD_SERV  = {'result': {'status': 'OK', 'messages': ['Added Channel EPS-3.', 'Added ServiceDir EPS-METOP-ASCA-L21.']}} 
        OK_GET_SERV  = {'service_dirs': [{'name': 'EPS-METOP-ASCA-L21', 'channel': 'EPS-3'}]}  
        OK_DEL_SERV  = {'status': 'OK', 'messages': 'service_dir EPS-METOP-ASCA-L21 deleted'}  
        OK_NO_SERV   = {'service_dirs': []} 
        OK_NO_CHAN   = {'channels': [{'min_rate': '400000', 'multicast_address': '224.223.222.223:4711', 'max_rate': '1', 'channel_function': 'AIDA-16', 'name': 'EPS-3'}]} 
       
        
        print("\n")
       
        self._clean_db()
        
        the_file = open("%s/service.json" % (DATA_DIR))
        json_text = the_file.read()
        
        #get client
        client = eumetsat.viewer.flask_server.app.test_client()
        
        #add product
        print("=> add services \n")
        returned_val = client.post('/servicedirs', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_ADD_SERV, "Fail when adding service dir. \n%s \nis different from \n%s" % (data, OK_ADD_SERV))
        
        #get products
        print("=> get services\n")
        returned_val = client.get("/servicedirs", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_GET_SERV, "Fail when getting service dir. \n%s \nis different from \n%s" % (data, OK_ADD_SERV))
        
        prod_id = 'EPS-METOP-ASCA-L21'
        
        #delete product
        print("=> delete services\n")
        returned_val = client.delete("/servicedirs/%s" % (prod_id), content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        self.assertDictEqual(data, OK_DEL_SERV, "Fail when deleting service dir. \n%s \nis different from \n%s" % (data, OK_ADD_SERV))
        
        # getting product one more time
        print("=> get services\n")
        returned_val = client.get("/servicedirs", content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        self.assertDictEqual(data, OK_NO_SERV, "Fail when getting service dir. \n%s \nis different from \n%s" % (data, OK_ADD_SERV))

        # getting product one more time
        print("=> get channel\n")
        returned_val = client.get("/channels", content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        self.assertDictEqual(data, OK_NO_CHAN, "Fail when getting channel. \n%s \nis different from \n%s" % (data, OK_NO_CHAN))

    
    def test_get_add_delete_product(self):
        """**********  add a product, get it and delete it **************"""
        
        OK_ADD_PROD  = {'result': {'status': 'OK', 'messages': ['Added Channel EPS-3.', 'Added ServiceDir EPS-METOP-ASCA-L1.', 'Added Product EO:EUM:DAT:METOP:ASCSZR1B.']}}
        OK_GET_PROD  = {'products': [{'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}]}
        OK_DEL_PROD  = {'status': 'OK', 'messages': ['product EO:EUM:DAT:METOP:ASCSZR1B deleted']}
        OK_NO_PROD   = {'products': []}
       
        print("\n")
       
        self._clean_db()
        
        the_file = open("%s/product.json" % (DATA_DIR))
        json_text = the_file.read()
        
        #get client
        client = eumetsat.viewer.flask_server.app.test_client()
        
        #add product
        print("=> add product \n")
        returned_val = client.post('/products', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_ADD_PROD, "Fail when adding product. Json dicts are different")
        
        #get products
        print("=> get products\n")
        returned_val = client.get("/products", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_GET_PROD, "Fail when getting product. \n%s \nis different from \n%s" % (data, OK_ADD_PROD))
        
        prod_id = 'EO:EUM:DAT:METOP:ASCSZR1B'
        
        #delete product
        print("=> delete product\n")
        returned_val = client.delete("/products/%s" % (prod_id), content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        self.assertDictEqual(data, OK_DEL_PROD, "Fail when deleting product. \n%s \nis different from \n%s" % (data, OK_ADD_PROD))
        
        # getting product one more time
        print("=> get product\n")
        returned_val = client.get("/products", content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        self.assertDictEqual(data, OK_NO_PROD, "Fail when getting product. \n%s \nis different from \n%s" % (data, OK_ADD_PROD))

    def test_update_product(self):
        """********** Update products **************"""
        
        OK_ADD_PROD     = {'result': {'status': 'OK', 'messages': ['Added Channel EPS-3.', 'Added ServiceDir EPS-METOP-ASCA-L1.', 'Added Product EO:EUM:DAT:METOP:ASCSZR1B.']}}
        OK_GET_PROD     = {'products': [{'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}]} 
        OK_UPDATE_PROD  = {'result': ['Update Product EO:EUM:DAT:METOP:ASCSZR1B']}
        OK_UPDATED_PROD = {'products': [{'description': 'UPDATED DESCRIPTION', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}, {'name': 'ascat_bufr4', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': [], 'type': 'bufr', 'size': '500TB'}]}, 'geonetcast-info': {'files': [{'name': 'ascat_bufr5', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['geonetcast-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}]}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info', 'geonetcast-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'updated product'}]}    
        
        print("\n")
       
        self._clean_db()
        
        the_file = open("%s/product.json" % (DATA_DIR))
        json_text = the_file.read()
        
        #get client
        client = eumetsat.viewer.flask_server.app.test_client()
        
        #add product
        print("=> add product \n")
        returned_val = client.post('/products', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        print(data)
      
        self.assertDictEqual(data, OK_ADD_PROD, "Fail when adding product. Json dicts are different")
        
        #get products
        print("=> get products\n")
        returned_val = client.get("/products", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_GET_PROD, "Fail when getting product. \n%s \nis different from \n%s" % (data, OK_GET_PROD))
        
        print("=> update product \n")
        the_file = open("%s/updated_product.json" % (DATA_DIR))
        json_text = the_file.read()
        
        returned_val = client.put('/products', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_UPDATE_PROD, "Fail when adding product. Json dicts are different")
        
        #get products
        print("=> get products\n")
        returned_val = client.get("/products", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_UPDATED_PROD, "Fail when getting product. \n%s \nis different from \n%s" % (data, OK_UPDATED_PROD))
   
    def test_file_product(self):
        """********** test the file fonctionality **************"""     
        OK_ADD_PROD     = {'result': {'status': 'OK', 'messages': ['Added Channel EPS-3.', 'Added ServiceDir EPS-METOP-ASCA-L1.', 'Added Product EO:EUM:DAT:METOP:ASCSZR1B.']}}
        
        OK_GET_PROD     = {'products': [{'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}]} 
        
        OK_ADD_FILE     = {'result': {'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}, {'name': 'new_file1', 'regexpr': 'nf.bufr', 'dis_type': ['eumetcast-info', 'gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '1GB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}, {'name': 'new_file1', 'regexpr': 'nf.bufr', 'dis_type': ['eumetcast-info', 'gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '1GB'}, {'name': 'new_file', 'regexpr': 'a.bufr', 'dis_type': ['eumetcast-info'], 'service_dir': [], 'type': 'bufr', 'size': '200MB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}}
        
        # add more diss types
        OK_UPDATE_FILE  = {'result': {'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}, {'name': 'new_file1', 'regexpr': 'nf.bufr', 'dis_type': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '1GB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}, {'name': 'new_file1', 'regexpr': 'nf.bufr', 'dis_type': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '1GB'}, {'name': 'new_file', 'regexpr': 'a.bufr', 'dis_type': ['eumetcast-info'], 'service_dir': [], 'type': 'bufr', 'size': '200MB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}, {'name': 'new_file1', 'regexpr': 'nf.bufr', 'dis_type': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '1GB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}}     
        
        OK_UPDATE1_FILE = {'result': {'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}, {'name': 'new_file1', 'regexpr': 'nff.bufr', 'dis_type': ['eumetcast-info', 'gts-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'grib', 'size': '1GB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}, {'name': 'new_file1', 'regexpr': 'nff.bufr', 'dis_type': ['eumetcast-info', 'gts-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'grib', 'size': '1GB'}, {'name': 'new_file', 'regexpr': 'a.bufr', 'dis_type': ['eumetcast-info'], 'service_dir': [], 'type': 'bufr', 'size': '200MB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}}  
        
        print("\n")
       
        self._clean_db()
        
        the_file = open("%s/product.json" % (DATA_DIR))
        json_text = the_file.read()
        
        #get client
        client = eumetsat.viewer.flask_server.app.test_client()
        
        #add product
        print("=> add product \n")
        returned_val = client.post('/products', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        print(data)
      
        self.assertDictEqual(data, OK_ADD_PROD, "Fail when adding product. Json dicts are different")
        
        #get products
        print("=> get products\n")
        returned_val = client.get("/products", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_GET_PROD, "Fail when getting product. \n%s \nis different from \n%s" % (data, OK_GET_PROD))
        
        print("=> add more files in product \n")
        the_file = open("%s/simple_file.json" % (DATA_DIR))
        json_text = the_file.read()
        returned_val = client.post('/product/EO:EUM:DAT:METOP:ASCSZR1B/files', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_ADD_FILE, "Fail when getting product. \n%s \nis different from \n%s" % (data, OK_ADD_FILE))
        
        #update a file
        print("=> update a file (add more diss types) \n")
        the_file = open("%s/update_file.json" % (DATA_DIR))
        json_text = the_file.read()
        returned_val = client.put("/product/EO:EUM:DAT:METOP:ASCSZR1B/files", data=json_text, content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_UPDATE_FILE, "Fail when getting product. \n%s \nis different from \n%s" % (data, OK_UPDATE_FILE))
   
        #update files again
        print("=> update files again (remove diss types) \n")
        the_file = open("%s/update1_file.json" % (DATA_DIR))
        json_text = the_file.read()
        returned_val = client.put("/product/EO:EUM:DAT:METOP:ASCSZR1B/files", data=json_text, content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_UPDATE1_FILE, "Fail when getting product.\n produced result\n%s \nis different from expected\n%s" % (data, OK_UPDATE1_FILE))
   
    def test_delete_file_product(self):
        """********** test the file deletion **************"""   
        OK_ADD_PROD          = {'result': {'status': 'OK', 'messages': ['Added Channel EPS-3.', 'Added ServiceDir EPS-METOP-ASCA-L1.', 'Added Product EO:EUM:DAT:METOP:ASCSZR1B.']}}
        
        OK_GET_PROD          = {'products': [{'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': [{'name': 'ascat_bufr', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['gts-info'], 'service_dir': [], 'type': 'bufr', 'size': '200KB'}]}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'gts-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}]} 
        
        OK_DELETE_FILE       = {'status': 'OK', 'messages': 'FileInfo ascat_bufr removed from the database'} 
        
        OK_GET_PROD2         = {'products': [{'description': 'The prime objective of the Advanced SCATterometer (ASCAT) is to measure wind speed and direction over the oceans, and the main operational application is the assimilation of ocean winds in NWP models. Other operational applications, based on the use of measurements of the backscattering coefficient, are sea ice edge detection and monitoring, monitoring sea ice, snow cover, soil moisture and surface parameters. The product is available from the archive in 2 different spatial resolutions; 25 km and 12.5 km. Note that some of the data are reprocessed. Please refer to the associated product validation reports or product release notes for further information.', 'gts-info': {'files': []}, 'eumetcast-info': {'files': [{'name': 'ascat_bufr1', 'regexpr': 'ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'bufr', 'size': '200KB'}, {'name': 'ascat_native', 'regexpr': 'ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z', 'dis_type': ['eumetcast-info'], 'service_dir': ['EPS-METOP-ASCA-L1'], 'type': 'native', 'size': '740KB'}]}, 'geonetcast-info': {'files': []}, 'uid': 'EO:EUM:DAT:METOP:ASCSZR1B', 'distribution': ['eumetcast-info', 'data-centre-info'], 'data-centre-info': {'files': [{'name': 'ascat_native_large', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'native', 'size': '25MB'}, {'name': 'ascat_hdf5eps', 'regexpr': '', 'dis_type': ['data-centre-info'], 'service_dir': [], 'type': 'hdf5eps', 'size': '27MB'}]}, 'name': 'ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)'}]} 
        
        KO_DELETE_SAME_FILE  = {'status': 'KO', 'messages': ["Product EO:EUM:DAT:METOP:ASCSZR1B doesn't contain the file info ascat_bufr"]}
        
        KO_NON_EXISTING_PROD = {'status': 'KO', 'messages': ["Product NON:EO:EUM:DAT:METOP:ASCSZR1B doesn't exist"]} 
         
        
        print("\n")
       
        self._clean_db()
        
        the_file = open("%s/product.json" % (DATA_DIR))
        json_text = the_file.read()
        
        #get client
        client = eumetsat.viewer.flask_server.app.test_client()
        
        #add product
        print("=> add product \n")
        returned_val = client.post('/products', data=json_text, content_type = 'application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        print(data)
      
        self.assertDictEqual(data, OK_ADD_PROD, "Fail when adding product. Json dicts are different")
        
        #get products
        print("=> get products\n")
        returned_val = client.get("/products", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_GET_PROD, "Failed. \n%s \nis different from \n%s" % (data, OK_GET_PROD))
        
        #delete file product
        print("=> delete file ascat_bufr in product EO:EUM:DAT:METOP:ASCSZR1B\n")
        returned_val = client.delete("/product/EO:EUM:DAT:METOP:ASCSZR1B/files/ascat_bufr", content_type='application/json')
        
        assert returned_val.mimetype == 'application/json'
        
        data = flask.json.loads(returned_val.data)
        
        self.assertDictEqual(data, OK_DELETE_FILE, "Failed. \n%s \nis different from \n%s" % (data, OK_DELETE_FILE))
        
        #get products
        print("=> get products\n")
        returned_val = client.get("/products", content_type='application/json')
        assert returned_val.mimetype == 'application/json'
        data = flask.json.loads(returned_val.data)
        
        expected = OK_GET_PROD2
        self.assertDictEqual(data, expected, "Failed. \n%s \nis different from \n%s" % (data, expected))
        
        
        #delete the same file product
        print("=> delete again file ascat bufr in product EO:EUM:DAT:METOP:ASCSZR1B\n")
        returned_val = client.delete("/product/EO:EUM:DAT:METOP:ASCSZR1B/files/ascat_bufr", content_type='application/json')
        
        assert returned_val.mimetype == 'application/json'
        
        data = flask.json.loads(returned_val.data)
        
        expected = KO_DELETE_SAME_FILE
        self.assertDictEqual(data, expected, "Failed. \n%s \nis different from \n%s" % (data, expected))
        
        #delete file from non existing product
        print("=> delete again file ascat bufr in from a non existing product")
        returned_val = client.delete("/product/NON:EO:EUM:DAT:METOP:ASCSZR1B/files/ascat_hdf5eps", content_type='application/json')
        
        assert returned_val.mimetype == 'application/json'
        
        data = flask.json.loads(returned_val.data)
        
        expected = KO_NON_EXISTING_PROD
        self.assertDictEqual(data, expected, "Failed. \n%s \nis different from \n%s" % (data, expected))
        
       
        
        