'''
Created on Sep 30, 2010

@author: guillaume.aubert@eumetsat.int
'''
import time
from sqlalchemy.orm import joinedload
from flask import Module, g, render_template, request, redirect, flash, url_for, jsonify, current_app


import eumetsat.common.utils as utils

import eumetsat.common.logging_utils as logging

from eumetsat.db.rodd_db import DAO, Channel, Product, ServiceDir, FileInfo, DistributionType

json_access = Module(__name__) #pylint:disable-msg=C0103

#set json_access logger
LOGGER = logging.LoggerFactory.get_logger("json_access")

def print_dict(a_dict, a_out, a_format="%-25s %s"):
    """ pretty print a dictionary """
    for (key, val) in a_dict.items():
        a_out.write(a_format % (str(key)+':', val))
        
def debug():
    import pdb; pdb.set_trace()

    #assert current_app.debug == False, "Don't panic! You're here by request of debug()"



def _add_new_file_product(session, uid, file_data):
    """ add new file product. Keep all existing ones and add the new one """
    messages = []
    product = session.query(Product).filter_by(internal_id=uid).first()
    if product:
        product.add_files(session, file_data)
        
        session.add(product)
        session.commit()
        
        return product.jsonize()
    else:
        messages.append("No product %s in RODD." % (uid))
    
    return { "status"         : "KO",
             "messages"       : messages
           }

def _update_files_in_product(session, uid, file_data):
    """ associate a given file with a product """
    messages = []
    product = session.query(Product).filter_by(internal_id=uid).first()
    if product:
        product.update_files(session, file_data)
        
        session.add(product)
        session.commit()
        
        return product.jsonize()
    else:
        messages.append("No product %s in RODD." % (uid))
    
    return { "status"         : "KO",
             "messages"       : messages
           }
   
    

def _add_jsonized_channels(session, data):
    """ Add a jsonized channels """
    #add channels if there are any
    messages = []

    for chan in data.get('channels', []):
        #if it doesn't exist create it
        if not session.query(Channel).filter_by(name=chan['name']).first():
            session.add(Channel(chan['name'], \
                                chan['multicast_address'],\
                                chan['min_rate'],\
                                chan['max_rate'],\
                                chan['channel_function']))
            
            messages.append("Added Channel %s." %(chan['name']))
        else:
            messages.append("Channel %s already exists." %(chan['name']))
    
    return messages

def _add_jsonized_serv_dir(session, data):
    """ Add a jsonized service directories """
    
    messages = []
    
    for serv_dir in data.get('service_dirs', []):
        if not session.query(ServiceDir).filter_by(name=serv_dir['name']).first():
            chan = session.query(Channel).filter_by(name=serv_dir['channel']).first()
            the_service = ServiceDir(serv_dir['name'], chan)
            session.add(the_service)
            messages.append("Added ServiceDir %s." %(serv_dir['name']))
        else:
            messages.append("ServiceDir %s already exists." %(serv_dir['name'])) 

    return messages

def _update_jsonized_products(session, data):
    """ update existing products with the given data """
    
    messages = []
    
    for prod in data.get('products', []):
        retrieved_product = session.query(Product).filter_by(internal_id=prod['uid']).first()
        if retrieved_product:
            #update all the attributes of the product except uid
            retrieved_product.update(prod, session)
            
            messages.append("Update Product %s" % (prod['uid']))
            
        else:
            messages.append("Product %s cannot be updated because it doesn't exist in RODD" % (prod['uid']))
    
    session.commit()
    
    return messages
            

def _add_jsonized_products(session, data):
    """ Add a jsonized product """
    
    messages = []
    
    try:
        # add channels if there are any
        messages.extend(_add_jsonized_channels(session, data))
        # commit channels add-ons
        session.commit()
            
        # add servdirs if there are any
        messages.extend(_add_jsonized_serv_dir(session, data))
        # commit service dirs add-ons
        session.commit()
        
        for prod in data.get('products', []):
            if not session.query(Product).filter_by(internal_id=prod['uid']).first():
                product = Product(prod['name'], prod['uid'], prod['description'], True if prod['distribution'] else False, "Operational")
    
                file_dict = {}
                
                # iterate over the list of distribution types:
                for the_type in DistributionType.TYPES:
                    for a_file in prod.get(the_type, { 'files' : []})['files']:
                        
                        #look for existing file-info
                        finfo = session.query(FileInfo).filter_by(name=a_file['name']).first()    
                        if not finfo:   
                            finfo = file_dict.get(a_file['name'], None) 
                            if not finfo:
                                #create file object
                                finfo = FileInfo(  a_file["name"], \
                                                   a_file.get("regexpr", ""), \
                                                   a_file.get("size",0), \
                                                   a_file.get("type",None)
                                                )
                          
                                
                                #add serviceDirs if there are any and if it is a eumetcast-info distribution type
                                if the_type == DistributionType.EUMETCAST:
                                    serv_dir_names = a_file.get("service_dir", None)
                                    if serv_dir_names: 
                                        for serv_dir_name in serv_dir_names:
                                            service_d = session.query(ServiceDir).filter_by(name=serv_dir_name).first()    
                                            finfo.service_dirs.append(service_d)
                        
                         
                        #add eumetcast distribution type
                        diss_type = session.query(DistributionType).filter_by(name=the_type).first() 
                        finfo.dis_types.append(diss_type)
                        
                        product.file_infos.append(finfo)
                        
                        file_dict[finfo.name] = finfo
                    
                session.add(product) 
                
                messages.append("Added Product %s." %(prod['uid']))
                LOGGER.info("Added Product %s." %(prod['uid']))
            else:
                messages.append("Product %s already exists." %(prod['uid']))
                LOGGER.info("Product %s already exists." %(prod['uid']))
                
        # commit session whatever has happened
        session.commit()
        
        return { "status" : "OK",
                 "messages"       : messages
               }
    
    except Exception, the_exception:  #pylint:disable-msg=W0703
        return { "status"         : "KO",
                 "messages"       : messages,
                 "error_messages" : the_exception,
                 "traceback"      : utils.get_exception_traceback()
               }

@json_access.route('/products/<uid>', methods=['GET','DELETE'])
def manage_product_with(uid):
    """ Restish get_product per uid """
    
    dao = DAO()
    if request.method == 'GET':
        # show the user profile for that user
        
        session = dao.get_session()
        
        the_products = { "products" : [] }
        
        #look for stars in uid and replace them with % for a like sql operation
        if uid.find('*'):
            if len(uid) == 1:
                product_table = dao.get_table("products")
                #get everything because user asked for *
                for product in session.query(Product).order_by(product_table.c.rodd_id):
                    the_products["products"].append(product.jsonize())  
            else:
                #restrict to the wildcard matching string
                uid = uid.replace('*', '%')
                for product in session.query(Product).filter(Product.internal_id.like(uid)):
                    the_products["products"].append(product.jsonize())   
        else:
            product = session.query(Product).filter_by(internal_id = uid).first()
            if product:
                the_products["products"].append(product.jsonize())
        
        return jsonify(the_products)
    
    elif request.method == 'DELETE':
        session = dao.get_session()
        product = session.query(Product).filter_by(internal_id = uid).first()
        
        if product:
            session.delete(product)
            session.commit()
            result = { "status" : "OK",
                        "messages"       : ["product %s deleted" % (uid)]
                      }
        else:
            result = { "status" : "KO",
                        "messages"       : ["product %s not in database" % (uid)]
                     }
            
        return jsonify(result)
    
@json_access.route('/channels/<name>', methods=['GET','DELETE'])
def manage_channel_with(name):
    """ Restish get_channels per name """
    
    dao = DAO()
    if request.method == 'GET':
        # show the user profile for that user
        
        session = dao.get_session()
        
        the_result = { "channels" : [] }
        
        #look for stars in uid and replace them with % for a like sql operation
        if name.find('*'):
            if len(name) == 1:
                channel_table = dao.get_table("channels")
                #get everything because user asked for *
                for channel in session.query(Channel).order_by(channel_table.c.rodd_id):
                    the_result ["channels"].append(channel.jsonize())  
            else:
                #restrict to the wildcard matching string
                name = name.replace('*', '%')
                for channel in session.query(Channel).filter(Channel.name.like(name)):
                    the_result["channels"].append(channel.jsonize())   
        else:
            channel = session.query(Channel).filter_by(name = name).first()
            if channel:
                the_result["channels"].append(channel.jsonize())
        
        return jsonify(the_result)
    
    elif request.method == 'DELETE':
        session = dao.get_session()
        channel = session.query(Channel).filter_by(name = name).first()
        
        if channel:
            session.delete(channel)
            session.commit()
            result = { "status" : "OK",
                        "messages"       : ["channel %s deleted" % (name)]
                      }
        else:
            result = { "status" : "KO",
                        "messages"       : ["channel %s not in database" % (name)]
                     }
            
        return jsonify(result)

@json_access.route('/channels', methods=['GET','POST'])
def get_all_channels():
    """ Restish return all channels information """
    
    dao = DAO()
    if request.method == 'GET':
        
        session = dao.get_session()
        
        channel_table = dao.get_table("channels")
        
        the_channels = { "channels" : [] }
        
        for channel in session.query(Channel).order_by(channel_table.c.chan_id):
            LOGGER.info("channel = %s" %(channel))
            if channel :
                the_channels["channels"].append(channel.jsonize()) 
          
        session.close()
        
        return jsonify(the_channels)
    
    elif request.method == 'POST':
        data = request.json
        return jsonify(result=_add_jsonized_products(dao.get_session(), data))


@json_access.route('/servicedirs', methods=['GET','POST'])
def get_all_servicedirs():
    """ Restish return all servicedirs information """

    dao = DAO()
    if request.method == 'GET':
        
        session = dao.get_session()
        
        servicedirs_table = dao.get_table("service_dirs")
        
        the_result = { "service_dirs" : [] }
        
        probe_t1 = time.time()
        for servdir in session.query(ServiceDir).order_by(servicedirs_table.c.serv_id).options(joinedload('channel')):
            the_result["service_dirs"].append(servdir.jsonize())
        probe_t2 = time.time()
       
        LOGGER.info("sql request and jsonizing time %f\n" %(probe_t2-probe_t1))
        
        session.close()
        
        return jsonify(the_result)
       
    
    elif request.method == 'POST':
        data = request.json
        return jsonify(result=_add_jsonized_products(dao.get_session(), data))

@json_access.route('/servicedirs/<name>', methods=['GET','DELETE'])
def manager_servicedir_with(name):
    """ Restish get_channels per name """
    
    dao = DAO()
    if request.method == 'GET':
        # show the user profile for that user
        session = dao.get_session()
        
        servicedirs_table = dao.get_table("service_dirs")
        
        the_result = { "service_dirs" : [] }
        
        #look for stars in uid and replace them with % for a like sql operation
        if name.find('*'):
            if len(name) == 1:
                #get everything because user asked for *
                for servdir in session.query(ServiceDir).order_by(servicedirs_table.c.serv_id):
                    the_result ["service_dirs"].append(servdir.jsonize())  
            else:
                #restrict to the wildcard matching string
                name = name.replace('*', '%')
                for servdir in session.query(ServiceDir).filter(ServiceDir.name.like(name)).order_by(servicedirs_table.c.serv_id):
                    the_result["service_dirs"].append(servdir.jsonize())   
        else:
            servdir = session.query(ServiceDir).filter_by(name = name).first()
            if servdir:
                the_result["service_dirs"].append(servdir.jsonize())
        
        return jsonify(the_result)
    
    elif request.method == 'DELETE':
        session = dao.get_session()
        servdir = session.query(ServiceDir).filter_by(name = name).first()
        
        if servdir:
            session.delete(servdir)
            session.commit()
            result = { "status" : "OK",
                        "messages"       : "service_dir %s deleted" % (name)
                      }
        else:
            result = { "status" : "KO",
                        "messages"       : "service_dir %s not in database" % (name)
                     }
            
        return jsonify(result)


@json_access.route('/product/<uid>/files', methods=['GET','PUT','POST'])
def get_all_files_for_product(uid):
    """ manage files in a product. POST add a new file, PUT update an existing one, GET get a file """
    
    dao = DAO()
    #get products
    if request.method == 'GET':
        result = { "files" : [] }
        
        session = dao.get_session()
         
        product = session.query(Product).filter_by(internal_id=uid).first()
    
        if product:
            
            for t_file in product.file_infos:
                result['files'].append(t_file.jsonize())
               
        session.close()
        return jsonify(result)
    
    #insert new products
    elif request.method == 'POST':
        data = request.json
        session = dao.get_session()
        res     = _add_new_file_product(dao.get_session(), uid, data)
        
        return jsonify(result=res)
    #update existing products
    elif request.method == 'PUT':
        data = request.json
        
        res  = _update_files_in_product(dao.get_session(), uid, data)
        
        return jsonify(result=res)

@json_access.route('/product/<uid>/files/<name>', methods=['DELETE'])
def delete_files_for_product(uid, name):
    """ delete files for a specific product """
    dao = DAO()
    session = dao.get_session()
         
    product = session.query(Product).filter_by(internal_id=uid).first()
    
    messages = []
    
    if product:
        # be sure that the file is within the product
        if product.contains_file(name):
            finfo = session.query(FileInfo).filter_by(name=name).first()
            
            if finfo:
                
                session.delete(finfo)
                session.commit()
            
                return  jsonify({ "status" : "OK",
                          "messages" : "FileInfo %s removed from the database" % (name)
                        })
            else:
                messages.append("FileInfo %s doesn't exist" % (name))
             
        else:
            messages.append("Product %s doesn't contain the file info %s" % (uid, name))
        
    else:
        messages.append("Product %s doesn't exist" %(uid))
    
    
    
    return jsonify({ "status" : "KO",
                 "messages"       : messages
           })
    
@json_access.route('/products', methods=['GET','POST','PUT'])
def get_all_products():
    """ Restish return all products information """
    
    #get products
    dao = DAO()
    if request.method == 'GET':
        session = dao.get_session()
        
        product_table = dao.get_table("products")
        
        the_products = { "products" : [] }
       
        probe_t1 = time.time()
        res = session.query(Product).order_by(product_table.c.rodd_id).options(joinedload('file_infos'))
        probe_t2 = time.time()
       
        LOGGER.info("#### sql request %f\n" %(probe_t2-probe_t1))
        
        probe_t1 = time.time()
        for product in res:
            the_products["products"].append(product.jsonize())
        
        probe_t2 = time.time()
       
        LOGGER.info("#### creating products %f\n" %(probe_t2-probe_t1))
           
        session.close()
        probe_t1 = time.time()
        json_res = jsonify(the_products)
        probe_t2 = time.time()
       
        LOGGER.info("#### jsonify %f\n" %(probe_t2-probe_t1))
        
        return json_res
    #insert new products
    elif request.method == 'POST':
        data = request.json
        session = dao.get_session()
        res     = _add_jsonized_products(session, data)
        
        LOGGER.info("products = %s" %(res))
        
        return jsonify(result=res)
    #update existing products: the policy is delete current object and add the new one
    elif request.method == 'PUT':
        data = request.json
        return jsonify(result=_update_jsonized_products(dao.get_session(), data))