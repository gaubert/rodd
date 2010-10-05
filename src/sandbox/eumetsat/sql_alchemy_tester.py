'''
Created on Sep 23, 2010

@author: gaubert
'''
import time
import datetime

import sqlalchemy
import simplejson as json

from sqlalchemy.orm import mapper, relationship, backref
from eumetsat.db.rodd_db import DAO, Channel, Product, ServiceDir, FileInfo

from eumetsat.viewer.views.json_access import _add_jsonized_products



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

def func_update_jsonised_products():
    """ update jsonized products """
    dao = DAO()
    
    session = dao.get_session()
    
    f = open('/homespace/gaubert/ecli-workspace/rodd/etc/json/product_example')
    
    product_dict = json.loads(f.read())
    
    #_add_jsonized_products(session, product_dict)
    
    # update product 
    for prod in product_dict.get('products', []):
        
        prod['name']       = 'title with time %s' % (datetime.datetime.now())
        prod['description'] = 'my description with time %s' % (datetime.datetime.now())
        
        retrieved_prod = session.query(Product).filter_by(internal_id='TEST:EO:EUM:DAT:METOP:ASCSZR1B').first()
        
        retrieved_prod.update(prod)
        
        #update the product
        if retrieved_prod:
            retrieved_prod.internal_id = 'TEST:EO:EUM:DAT:METOP:ASCSZRIB'
            retrieved_prod.title = prod['name']
            retrieved_prod.description = prod['description']
            
            print("retrieved prod modified = %s\n" % (retrieved_prod))
            
            session.add(retrieved_prod)
            session.commit()
           
    
    

def func_jsonised_test():
    """ func test """
     
    f = open('/homespace/gaubert/ecli-workspace/rodd/etc/json/product_example')
    
    product2 = f.read()

    prod_dir = json.loads(product2)
    
    a_dao = DAO()
    
    session = a_dao.get_session()
    
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
                 
            
            for a_file in prod['gts-info']['files']:
                 
                #look for existing file-info
                finfo = session.query(FileInfo).filter_by(name=a_file['name']).first()    
                if not finfo:    
                    finfo = file_dict.get(a_file['name'], None)
                    if not finfo:             
                        #create file object
                        finfo = FileInfo(a_file["name"], \
                                           a_file.get("regexpr", ""), \
                                           a_file["size"], \
                                           a_file["type"])
                
                product.gts_infos.append(finfo)
            
            for a_file in prod['data-centre-info']['files']:
                 
                #look for existing file-info
                finfo = session.query(FileInfo).filter_by(name=a_file['name']).first()    
                if not finfo:    
                    finfo = file_dict.get(a_file['name'], None)
                    if not finfo:          
                        #create file object
                        finfo = FileInfo(  a_file["name"], \
                                           a_file.get("regexpr", ""), \
                                           a_file["size"], \
                                           a_file["type"])
                
                product.data_centre_infos.append(finfo)
            
            session.add(product)    
                  
    session.commit()

    session.close()

if __name__ == '__main__':
    func_update_jsonised_products()
    #func_jsonised_test()
    #func_return_jsonised_products()