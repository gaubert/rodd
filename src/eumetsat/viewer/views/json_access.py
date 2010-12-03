'''
Created on Sep 30, 2010

@author: guillaume.aubert@eumetsat.int
'''
from flask import Module, g, render_template, request, redirect, flash, url_for, jsonify

import eumetsat.common.utils as utils

import eumetsat.common.logging_utils as logging

from eumetsat.db.rodd_db import DAO, Channel, Product, ServiceDir, FileInfo, DistributionType

json_access = Module(__name__)

#set json_access logger
LOGGER = logging.LoggerFactory.get_logger("json_access")

def printDict(di, out, format="%-25s %s"):
    """ pretty print a dictionary """
    for (key, val) in di.items():
        out.write(format % (str(key)+':', val))

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

def _update_file_in_product(session, uid, file_name, file_data):
    """ associate a given file with a product """
    
    messages = []
    
    product = session.query(Product).filter_by(internal_id=uid).first()
    
    if product:
        tuple = product.contains_file(file_name)
        
        if tuple:
            grp_list, file = tuple
            file.update(session, file_data)
            
            #update File independently of the product
            session.add(product)
            session.commit()
            
            messages.append("Updated file '%s' for product %s" % (file_name, uid))
            
            return { "status"         : "OK",
                     "messages"       : messages
                   }
        else:
            messages.append("No file %s in product %s." % (file_name, product.internal_id))
    else:
        messages.append("No product %s in RODD." % (uid))
        
    return { "status"         : "KO",
             "messages"       : messages
           }
    

def _add_jsonized_channels(session, data):
    """ Add a jsonized channels """
    #add channels if there are any
    messages = []
    
    channel_table = g.dao.get_table("channels")

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
                    for a_file in prod.get(the_type,{ 'files' : []})['files']:
                        
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
                          
                                
                                #add serviceDirs if there are any and if it is a eumetcast-info distribution type
                                if the_type == DistributionType.EUMETCAST:
                                    serv_dir_names = a_file.get("service_dir", None)
                                     
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
    
    except Exception, the_exception:
        return { "status"         : "KO",
                 "messages"       : messages,
                 "error_messages" : the_exception,
                 "traceback"      : utils.get_exception_traceback()
               }

@json_access.route('/products/<uid>', methods=['GET','DELETE'])
def manage_product_with(uid):
    """ Restish get_product per uid """
    
    if request.method == 'GET':
        # show the user profile for that user
        session = g.dao.get_session()
        
        the_products = { "products" : [] }
        
        #look for stars in uid and replace them with % for a like sql operation
        if uid.find('*'):
            if len(uid) == 1:
                product_table = g.dao.get_table("products")
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
        session = g.dao.get_session()
        product = session.query(Product).filter_by(internal_id = uid).first()
        
        if product:
            session.delete(product)
            session.commit()
            result = { "status" : "OK",
                        "messages"       : ["product %s deleted" %(uid)]
                      }
        else:
            result = { "status" : "KO",
                        "messages"       : ["product %s not in database" % (uid)]
                     }
            
        return jsonify(result)
    
@json_access.route('/channels/<name>', methods=['GET','DELETE'])
def manage_channel_with(name):
    """ Restish get_channels per name """
    
    if request.method == 'GET':
        # show the user profile for that user
        session = g.dao.get_session()
        
        the_result = { "channels" : [] }
        
        #look for stars in uid and replace them with % for a like sql operation
        if name.find('*'):
            if len(name) == 1:
                channel_table = g.dao.get_table("channels")
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
        session = g.dao.get_session()
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
    
    if request.method == 'GET':
        session = g.dao.get_session()
        
        channel_table = g.dao.get_table("channels")
        
        the_channels = { "channels" : [] }
        
        for channel in session.query(Channel).order_by(channel_table.c.chan_id):
            LOGGER.info("channel = %s" %(channel))
            if channel :
                the_channels["channels"].append(channel.jsonize()) 
          
        session.close()
        
        return jsonify(the_channels)
    
    elif request.method == 'POST':
        data = request.json
        return jsonify(result=_add_jsonized_products(g.dao.get_session(), data))

@json_access.route('/servicedirs', methods=['GET','POST'])
def get_all_servicedirs():
    """ Restish return all servicedirs information """
    
    if request.method == 'GET':
        session = g.dao.get_session()
        
        servicedirs_table = g.dao.get_table("service_dirs")
        
        the_result = { "service_dirs" : [] }
        
        for servdir in session.query(ServiceDir).order_by(servicedirs_table.c.serv_id):
            the_result["service_dirs"].append(servdir.jsonize())
        
        session.close()
        
        return jsonify(the_result)
    
    elif request.method == 'POST':
        data = request.json
        return jsonify(result=_add_jsonized_products(g.dao.get_session(), data))

@json_access.route('/servicedirs/<name>', methods=['GET','DELETE'])
def manager_servicedir_with(name):
    """ Restish get_channels per name """
    
    if request.method == 'GET':
        # show the user profile for that user
        session = g.dao.get_session()
        
        servicedirs_table = g.dao.get_table("service_dirs")
        
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
        session = g.dao.get_session()
        servdir = session.query(ServiceDir).filter_by(name = name).first()
        
        if servdir:
            session.delete(servdir)
            session.commit()
            result = { "status" : "OK",
                        "messages"       : "service_dir %s deleted" %(name)
                      }
        else:
            result = { "status" : "KO",
                        "messages"       : "service_dir %s not in database" % (name)
                     }
            
        return jsonify(result)

@json_access.route('/product/<uid>/files', methods=['GET','PUT','POST'])
def get_all_files_for_product(uid):
    """ manage files in a product. POST add a new file, PUT update an existing one, GET get a file """
    
    #get products
    if request.method == 'GET':
        result = { "files" : [] }
        
        session = g.dao.get_session()
         
        product = session.query(Product).filter_by(internal_id=uid).first()
    
        if product:
            
            for t_file in product.file_infos:
                result['files'].append(t_file.jsonize())
               
        session.close()
        return jsonify(result)
    
    #insert new products
    elif request.method == 'POST':
        data = request.json
        session = g.dao.get_session()
        res     = _add_new_file_product(session, uid, data)
        
        return jsonify(result=res)
    #update existing products
    elif request.method == 'PUT':
        data = request.json
        return jsonify(result=_update_jsonized_products(g.dao.get_session(), data))
    

@json_access.route('/products', methods=['GET','POST','PUT'])
def get_all_products():
    """ Restish return all products information """
    
    #get products
    if request.method == 'GET':
        session = g.dao.get_session()
        
        product_table = g.dao.get_table("products")
        
        the_products = { "products" : [] }
        for product in session.query(Product).order_by(product_table.c.rodd_id):
            the_products["products"].append(product.jsonize())
           
        session.close()
        return jsonify(the_products)
    #insert new products
    elif request.method == 'POST':
        data = request.json
        session = g.dao.get_session()
        res     = _add_jsonized_products(session, data)
        
        LOGGER.info("products = %s" %(res))
        
        return jsonify(result=res)
    #update existing products: the policy is delete current object and add the new one
    elif request.method == 'PUT':
        data = request.json
        return jsonify(result=_update_jsonized_products(g.dao.get_session(), data))