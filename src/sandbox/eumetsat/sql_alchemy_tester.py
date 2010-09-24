'''
Created on Sep 23, 2010

@author: gaubert
'''
import sqlalchemy
from sqlalchemy.orm import mapper, relationship
from eumetsat.db import connections

class Product(object):
    """ Product Object """
    def __init__(self, title, internal_id, reg_expr, disseminated, status):
        self.title           = title
        self.internalID      = internal_id
        self.regularExpr     = reg_expr
        self.isDisseminated  = disseminated
        self.status          = status
    
    def __repr__(self):
        return "<Product('%s','%s', '%s', '%s', '%s')>" % (self.title, self.internalID, self.regularExpr, self.isDisseminated, self.status)

class ServiceDir(object):
    """ServiceDir object """
    def __init__(self, name, chan_id):
        self.name   = name
        self.chanID = chan_id
    
    def __repr__(self):
        return "<ServiceDir('%s','%s')>" % (self.name, self.chanID)

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
    
    #create many to many relation table
    # beware add foreign key constraints manually as they do not exist in MYSQL
    products_2_servdirs_table = sqlalchemy.Table('products_2_servdirs', metadata, sqlalchemy.ForeignKeyConstraint(['roddID'], ['products.roddID']), sqlalchemy.ForeignKeyConstraint(['servID'], ['service_dirs.servID']), autoload = True)

    # create many to many relation ship between service_dirs and products with products_2_servdirs assoc table
    mapper(Product, product_table, properties={
    'service_dirs': relationship(ServiceDir, secondary=products_2_servdirs_table)
    })
  
    # mapp ServiceDir obj to service_dirs table
    mapper(ServiceDir, service_dirs_table)
  
  
    # instanciate everything => create tests
    product1 = Product("MyTitle", "EUM:DASD:WERT", "file_DDDMMMGG.bufr", True, "Operational")
    
    service1 = ServiceDir("ServiceDir",134)
    
    service2 = ServiceDir("AnotherServiceDir",136)
    
    product1.service_dirs.append(service1)
    product1.service_dirs.append(service2)
    
    session = conn.get_session()
    session.add(product1)
    session.commit()

    


if __name__ == '__main__':
    func_test()