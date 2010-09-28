'''
Created on Sep 23, 2010

@author: gaubert
'''
import time

import sqlalchemy
from sqlalchemy.orm import mapper, relationship
from eumetsat.db import connections



class Product(object):
    """ Product Object """
    def __init__(self, title, internal_id, reg_expr, disseminated, status):
        self.rodd_id            = None
        self.title              = title
        self.internal_id        = internal_id
        self.regular_expr       = reg_expr
        self.is_disseminated    = disseminated
        self.status             = status
        self.data_centre_infos  = []
        self.gts_infos          = []
        self.eumetcast_infos    = []
        self.geonetcast_infos   = []
  
    def __repr__(self):
        return "<Product(%s'%s', '%s', '%s', '%s', '%s', files= [ eumetcast = ('%s'), gts = ('%s'), data_centre= ('%s'), geonetcast = ('%s') )>" % ( ( "'rodd_id:%s', " % (self.rodd_id if self.rodd_id else "")), self.title, self.internal_id, self.regular_expr, self.is_disseminated, self.status, self.eumetcast_infos, self.gts_infos, self.data_centre_infos, self.geonetcast_infos)

class ServiceDir(object):
    """ServiceDir object """
    def __init__(self, name, chan_id):
        self.serv_id     = None
        self.name        = name
        self.chan_id     = chan_id
    
    def __repr__(self):
        return "<ServiceDir('%s', '%s')>" % (self.name, self.chan_id)
    
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

def func_test():
    """ func test """
    conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
    conn.connect()
    
    #load metadata
    metadata = conn.get_metadata()
    
    # load product table
    product_table = sqlalchemy.Table('products', metadata, autoload = True)
    
    # load service dirs table
    service_dirs_table = sqlalchemy.Table('service_dirs', metadata, autoload= True)
    
    # load file_info table
    file_info_table = sqlalchemy.Table('file_info', metadata, autoload= True)
    
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
    func_test()