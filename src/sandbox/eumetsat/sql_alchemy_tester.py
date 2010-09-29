'''
Created on Sep 23, 2010

@author: gaubert
'''
import time

import sqlalchemy
import simplejson as json

from sqlalchemy.orm import mapper, relationship, backref
from eumetsat.db import connections



class Product(object):
    """ Product Object """
    def __init__(self, title, internal_id, description, disseminated, status):
        self.rodd_id            = None
        self.title              = title
        self.internal_id        = internal_id
        self.description        = description
        self.is_disseminated    = disseminated
        self.status             = status
        self.data_centre_infos  = []
        self.gts_infos          = []
        self.eumetcast_infos    = []
        self.geonetcast_infos   = []
  
    def __repr__(self):
        return "<Product(%s'%s', '%s', '%s', '%s', '%s', files= [ eumetcast = ('%s'), gts = ('%s'), data_centre= ('%s'), geonetcast = ('%s') )>" \
               % ( ( "'rodd_id:%s', " % (self.rodd_id if self.rodd_id else "")), \
                     self.title, self.internal_id, \
                     self.description ,\
                     self.is_disseminated, \
                     self.status, \
                     self.eumetcast_infos, \
                     self.gts_infos, \
                     self.data_centre_infos, \
                     self.geonetcast_infos)
    
    def jsonize(self):
        
        result = {}
        
        result["name"]         = self.title 
        result["uid"]          = self.rodd_id
        result["description"]  = self.description
        result["distribution"] = []
        
        
        result["eumetcast-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "eumetcast-info" not in result["distribution"]:
                result["distribution"].append("eumetcast-info")
            
            result["eumetcast-info"]["files"].append(finfo.jsonize())
            
        
        result["gts-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "gts-info" not in result["distribution"]:
                result["distribution"].append("gts-info")
            
            result["gts-info"]["files"].append(finfo.jsonize())
        
        result["data-centre-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "data-centre-info" not in result["distribution"]:
                result["distribution"].append("data-centre-info")
            
            result["data-centre-info"]["files"].append(finfo.jsonize())
       
        result["geonetcast-info"] = { "files": [] }
        for finfo in self.eumetcast_infos:
            
            if "geonetcast-info" not in result["distribution"]:
                result["distribution"].append("geonetcast-info")
            
            result["geonetcast-info"]["files"].append(finfo.jsonize())
            
            
        return result
        
       

class ServiceDir(object):
    """ServiceDir object """
    def __init__(self, name, channel):
        self.serv_id     = None
        self.name        = name
        self.channel     = channel
    
    def __repr__(self):
        return "<ServiceDir('%s', '%s')>" % (self.name, self.channel)
    
class DistributionType(object):
    """ DistributionType object """
    def __init__(self, name):
        self.name     = name
    
    def __repr__(self):
        return "<DistributionType('%s')>" % (self.name)
    
class Channel(object):
    """ Channel object """
    
    def __init__(self, name, address, min_rate, max_rate, channel_function):
        self.chan_id           = None
        self.name              = name
        self.multicast_address = address
        self.min_rate          = min_rate
        self.max_rate          = max_rate
        self.channel_function  = channel_function
        
    def __repr__(self):
        return "<Channel('%s', '%s', '%s', '%s', '%s')>" % (self.name, self.multicast_address, self.min_rate, self.max_rate, self.channel_function)

class FileInfo(object):
    """ FileInfo object """
    def __init__(self, name, reg_expr, size, type):
         
        self.name         = name
        self.reg_expr     = reg_expr
        self.size         = size
        self.type         = type
        self.service_dirs = []
    
    def __repr__(self):
        return "<FileInfo('%s','%s', '%s', '%s', '%s')>" % (self.name, self.reg_expr, self.size, self.type, self.service_dirs)

    def jsonize(self):
        
        result = {"service_dir" : []}
        
        result["name"]        = self.name
        result["regexpr"]     = self.reg_expr
        result["size"]        = self.size
        result["type"]        = self.type
        
        for service_dir in self.service_dirs:
            result["service_dir"].append(service_dir.name)
            
        return result
        

class DAO(object):
    """ This is singleton """
    
    _instance = None
    _created   = False
    
    def __init__(self):
        
        if not DAO._created:
            self.conn     = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
            self.metadata = None
            self.tbl_dict = {}
            # load dao info
            self._load()
            
            DAO._created = True
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DAO, cls).__new__(
                                cls, *args, **kwargs)
            
        return cls._instance
 
    def _load(self):
        """ load the DAO info """
        self.conn.connect()
        
        self.metadata = self.conn.get_metadata()
        
        self.tbl_dict['products']      = sqlalchemy.Table('products', self.metadata, autoload = True)
    
        # load service dirs table
        self.tbl_dict['service_dirs']  = sqlalchemy.Table('service_dirs', self.metadata, \
                                                          sqlalchemy.ForeignKeyConstraint(['chan_id'], ['channels.chan_id']), \
                                                          autoload= True)
        
        # load file_info table
        self.tbl_dict['file_info']     = sqlalchemy.Table('file_info', self.metadata, autoload= True)
        
        # load file_info table
        self.tbl_dict['channels']      = sqlalchemy.Table('channels', self.metadata, autoload= True)
        
        
        #create many to many relation table
        # beware add foreign key constraints manually as they do not exist in MYSQL
        products_2_eumetcast_table      = sqlalchemy.Table('products_2_eumetcast', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_eumetcast'] = products_2_eumetcast_table
        
        products_2_geonetcast_table      = sqlalchemy.Table('products_2_geonetcast', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_geonetcast'] = products_2_geonetcast_table
        
        products_2_gts_table            = sqlalchemy.Table('products_2_gts', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_gts'] = products_2_gts_table
        
        products_2_data_centre_table    = sqlalchemy.Table('products_2_data_centre', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     autoload = True)
        
        self.tbl_dict['products_2_data_centre'] = products_2_data_centre_table
        
        file_2_servdirs_table           = sqlalchemy.Table('file_2_servdirs', self.metadata, \
                                                     sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                     sqlalchemy.ForeignKeyConstraint(['serv_id'], ['service_dirs.serv_id']), \
                                                     autoload = True)
        
        self.tbl_dict['file_2_servdirs'] = file_2_servdirs_table
    
        # create many to many relation ship between service_dirs and products with products_2_servdirs assoc table
        mapper(Product, self.tbl_dict['products'], properties={
        'data_centre_infos'  :  relationship(FileInfo,   secondary=products_2_data_centre_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'gts_infos'          :  relationship(FileInfo,   secondary=products_2_gts_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'eumetcast_infos'    :  relationship(FileInfo  , secondary=products_2_eumetcast_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        'geonetcast_infos'   :  relationship(FileInfo  , secondary=products_2_geonetcast_table, \
                                                         single_parent=True, cascade="all, delete, delete-orphan"),
        })
      
        # map file_info table
        mapper(FileInfo, self.tbl_dict['file_info'], properties={
        'service_dirs'   : relationship(ServiceDir, secondary=file_2_servdirs_table),
        })
        
        # map channels table
        mapper(Channel, self.tbl_dict['channels'])
        
        # map ServiceDir obj to service_dirs table
        mapper(ServiceDir, self.tbl_dict['service_dirs'], properties = {
            'channel': relationship(Channel, backref=backref('service_dirs', uselist=False))
        })
        

    def get_table(self, name):
        """ return table from the DAO """
        return self.tbl_dict[name]
    
    def get_session(self):
        """ return the session """
        return self.conn.get_session()
    
def func_return_jsonised_products():
    """ return a product that has been jsonised """
    
    # query all products
    dao = DAO()
    
    session = dao.get_session()
    
    product_table = dao.get_table("products")
    
    products = { "products" : [] }
    for product in session.query(Product).order_by(product_table.c.rodd_id):
        products["products"].append(product.jsonize())
    
    print("products = %s\n" %(products))
    
    session.close()
    

def func_jsonised_test():
    """ func test """
     
    f = open('/homespace/gaubert/ecli-workspace/rodd/etc/json/product_example')
    
    product2 = f.read()

    prod_dir = json.loads(product2)
    
    dao = DAO()
    
    session = dao.get_session()
    
    #add channels if there are any
    channels = prod_dir.get('channels', [])
    
    for chan in channels:
        #if it doesn't exist create it
        if not session.query(Channel).filter_by(name=chan['name']).first():
            session.add(Channel(chan['name'],chan['multicast_address'],chan['min_rate'],chan['max_rate'],chan['channel_function']))

    service_dirs = prod_dir.get('service_dirs', [])
    
    
    for serv_dir in service_dirs:
        if not session.query(ServiceDir).filter_by(name=serv_dir['name']).first():
            ch = session.query(Channel).filter_by(name=serv_dir['channel']).first()
            session.add(ServiceDir(serv_dir['name'], ch))
            
    products = prod_dir.get('products', [])
    
    for prod in products:
        if not session.query(Product).filter_by(internal_id='EO:EUM:DAT:METOP:ASCSZR1B').first():
            product = Product(prod['name'], prod['uid'], prod['description'], True if prod['distribution'] else False, "Operational")

            file_dict = {}

            for a_file in prod['eumetcast-info']['files']:
                 
                #create file object
                finfo = FileInfo(  a_file["name"], \
                                   a_file.get("regexpr", ""), \
                                   a_file["size"], \
                                   a_file["type"])
                  
                #add serviceDirs if there are any
                serv_dir_names = a_file.get("service_dir", None)
                 
                for serv_dir_name in serv_dir_names:
                    service_d = session.query(ServiceDir).filter_by(name=serv_dir_name).first()    
                    finfo.service_dirs.append(service_d)
                
                 
                product.eumetcast_infos.append(finfo)
                
                file_dict[finfo.name] = finfo
                 
            
            for file in prod['gts-info']['files']:
                 
                #look for existing file-info
                finfo = session.query(FileInfo).filter_by(name=file['name']).first()    
                if not finfo:    
                    finfo = file_dict.get(file['name'], None)
                    if not finfo:             
                        #create file object
                        finfo = FileInfo(file["name"], \
                                           file.get("regexpr", ""), \
                                           file["size"], \
                                           file["type"])
                
                product.gts_infos.append(finfo)
            
            for file in prod['data-centre-info']['files']:
                 
                #look for existing file-info
                finfo = session.query(FileInfo).filter_by(name=file['name']).first()    
                if not finfo:    
                    finfo = file_dict.get(file['name'], None)
                    if not finfo:          
                        #create file object
                        finfo = FileInfo(file["name"], \
                                           file.get("regexpr", ""), \
                                           file["size"], \
                                           file["type"])
                
                product.data_centre_infos.append(finfo)
            
            session.add(product)    
                  
    session.commit()

    session.close()

def func_test():
    """ func test """
    conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
    conn.connect()
    
    #load metadata
    metadata = conn.get_metadata()
    
    # load product table
    product_table      = sqlalchemy.Table('products', metadata, autoload = True)
    
    # load service dirs table
    service_dirs_table = sqlalchemy.Table('service_dirs', metadata, autoload= True)
    
    # load file_info table
    file_info_table    = sqlalchemy.Table('file_info', metadata, autoload= True)
    
    #create many to many relation table
    # beware add foreign key constraints manually as they do not exist in MYSQL
    products_2_eumetcast_table      = sqlalchemy.Table('products_2_eumetcast', metadata, \
                                                 sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                 sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                 autoload = True)
    
    products_2_geonetcast_table      = sqlalchemy.Table('products_2_geonetcast', metadata, \
                                                 sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                 sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                 autoload = True)
    
    products_2_gts_table            = sqlalchemy.Table('products_2_gts', metadata, \
                                                 sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                 sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                 autoload = True)
    
    products_2_data_centre_table    = sqlalchemy.Table('products_2_data_centre', metadata, \
                                                 sqlalchemy.ForeignKeyConstraint(['rodd_id'], ['products.rodd_id']), \
                                                 sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                 autoload = True)
    
    file_2_servdirs_table           = sqlalchemy.Table('file_2_servdirs', metadata, \
                                                 sqlalchemy.ForeignKeyConstraint(['file_id'], ['file_info.file_id']), \
                                                 sqlalchemy.ForeignKeyConstraint(['serv_id'], ['service_dirs.serv_id']), \
                                                 autoload = True)

    
    # create many to many relation ship between service_dirs and products with products_2_servdirs assoc table
    mapper(Product, product_table, properties={
    'data_centre_infos' :  relationship(FileInfo,   secondary=products_2_data_centre_table, single_parent=True, cascade="all, delete, delete-orphan"),
    'gts_infos'         :  relationship(FileInfo,   secondary=products_2_gts_table, single_parent=True, cascade="all, delete, delete-orphan"),
    'eumetcast_infos'   :  relationship(FileInfo  , secondary=products_2_eumetcast_table, single_parent=True, cascade="all, delete, delete-orphan"),
    'geonetcast_infos'   :  relationship(FileInfo  , secondary=products_2_geonetcast_table, single_parent=True, cascade="all, delete, delete-orphan"),
    })
  
    # mapp ServiceDir obj to service_dirs table
    mapper(ServiceDir, service_dirs_table)
    
    # mapp file_info table
    mapper(FileInfo, file_info_table, properties={
    'service_dirs'   : relationship(ServiceDir, secondary=file_2_servdirs_table),
    })
    
    # if product exist update it
    session = conn.get_session()
    
    product = session.query(Product).filter_by(internal_id='EO:EUM:DAT:METOP:ASCSZR1B').first() 

    if not product:
  
        # instanciate everything => create tests
        product1   = Product("ASCAT GDS Level 1 normalised backscatter (12.5 km node grid)", \
                           "EO:EUM:DAT:METOP:ASCSZR1B", \
                           "file_DDDMMMGG.bufr", \
                           True, \
                           "Operational")
        
        service1         = ServiceDir("EPS-METOP-ASCA-L1","EPS-3")
        
        #add eumetcast information
        finfo1 = FileInfo("ascat_bufr", \
                              "ascat_20070630_222400_metopa_03612_eps_o_125.l1_ bufr", \
                              200*1024, \
                              "bufr")
        
        finfo2 = FileInfo("ascat_native", \
                              "ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z", \
                              740*1024, \
                              "native")
        
        finfo1.service_dirs.append(service1)
        finfo2.service_dirs.append(service1)
         
        #add eumetcast files
        product1.eumetcast_infos.append(finfo1)
        product1.eumetcast_infos.append(finfo2)
        
        #add gts files
        product1.gts_infos.append(finfo1)
        
        finfo3 = FileInfo("ascat_native_large", \
                           None, \
                           25*1024*1024, \
                           "native")
        
        finfo4 = FileInfo("ascat_hdf5eps", \
                           None, \
                           27*1024*1024, \
                           "hdf5eps")
        
        product1.data_centre_infos.append(finfo3)
        product1.data_centre_infos.append(finfo4)
         
        session.add(product1)
    
    """
    
    else:
        # change operational status
        if product.status == "NonOperational":
            product.status = "Operational"
        else:
            product.status = "NonOperational"
        
        #remove one file and add a new one
        del product.file_infos[1]
        
        new_file_info = FileInfo("ascat_native.%s" %(time.time()), \
                              "ASCA_SZR_1B_M02_20070630222400Z_20070630222658Z_ N_O_20070701001421Z", \
                              740*1024, \
                              "native")
        
        service1= session.query(ServiceDir).filter_by(name="EPS-METOP-ASCA-L1").first()
        
        if not service1:
            print("Create the service")
            service1   = ServiceDir("EPS-METOP-ASCA-L1","EPS-3")
        
        new_file_info.service_dirs.append(service1)
        
        product.file_infos.append(new_file_info)
        
        session.add(product)
        
        session.commit()
    """
    
    # get all products
    for instance in session.query(Product).order_by(product_table.c.rodd_id): 
        print instance
        #session.delete(instance)
    
    session.commit()

    session.close()


if __name__ == '__main__':
    func_jsonised_test()
    func_return_jsonised_products()