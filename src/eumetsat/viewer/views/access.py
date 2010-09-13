'''
Created on Sep 13, 2010

@author: guillaume.aubert@eumetsat.int
'''

from flask import Module, render_template, request, redirect, flash, url_for

from eumetsat.db import connections

access = Module(__name__)

def _view_table(a_table_name):
    """
       Return the content of the sql table provided its name
    """
    try:
        conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
        conn.connect()
        
        # get metadata to get the columns names
        metadata = conn.get_table_metadata(a_table_name)
        
        col_names = [ dic["name"] for dic in metadata ]
    
        result = conn.execute("select * from %s" % (a_table_name) )
        
        output = render_template('generic_table.tpl', rows = result, heads = col_names, table= a_table_name)
        
        return output
    except Exception, the_exc:
        return the_exc

def _view_request_results(a_request_name, a_sql_req):
    
    """
       Return the content of the sql request provided its name
    """
    try:
        conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
        conn.connect()
        
        result = conn.execute(a_sql_req)
        
        col_names = result.keys()
       
        cols = result.fetchall()
        
        output = render_template('generic_table.tpl', rows = result, heads = col_names, table= a_request_name)
        
        return output
    
    except Exception, the_exc:
        app.logger.error(the_exc)
        return the_exc

@access.route('/tbl_products')
def view_tbl_products():
    """ 
       Viewer for products 
    """
    
    #return "table products"
    return _view_table("products")

@access.route('/format_type')
def view_format_type():
    """ 
       Viewer for format_type 
    """
    return _view_table("format_type")

@access.route('/channels')
def view_channels():
    """ 
       Viewer for channels 
    """
    return _view_table("channels")

@access.route('/families')
def view_families():
    """ 
       Viewer for families 
    """
    return _view_table("families")

@access.route('/service_dirs')
def view_services():
    """ 
       Viewer for service_dirs 
    """
    return _view_table("service_dirs")

@access.route('/products_2_servdirs')
def view_products_2_servdirs():
    """ 
       Viewer for products_2_servdirs 
    """
    #return view_table("products_2_servdirs")
    return _view_request_results("products2service", 
                                "select products.title as 'Product Name', \
                                service_dirs.name as 'Service Dir Name', \
                                products.roddID as 'roddID', \
                                service_dirs.servID as 'servID' \
                                from products, service_dirs, products_2_servdirs as p2s \
                                where p2s.roddID=products.roddID and p2s.servID=service_dirs.servID")
    
@access.route('/products_details')
def view_products_details():
    """ 
       Viewer for products_details 
    """
    #return view_table("products_2_servdirs")
    return _view_request_results("products details", 
                                "select products.internalID as 'Prod UID', service_dirs.name as 'Serv Name',\
                                        channels.name as 'Chan Name', families.name as 'Fam Name', products.title 'Prod Name', products.roddID as 'roddID' \
                                from products  \
                                left join (service_dirs, products_2_servdirs as p2s, \
                                           channels, families, servdirs_2_families)  \
                                on  ( p2s.roddID=products.roddID and p2s.servID=service_dirs.servID \
                                      and service_dirs.chanID = channels.chanID \
                                      and service_dirs.servID = servdirs_2_families.servID \
                                      and servdirs_2_families.famID = families.famID) \
                                order by products.roddID")
       

@access.route('/tbl_products_2_servdirs')
def view_tbl_products_2_servdirs():
    """ 
       Viewer table prod2servdirs
    """
    return _view_table("products_2_servdirs")

@access.route('/servdirs_2_families')
def view_servdirs_2_families():
    """ 
       Viewer for servdirs_2_families 
    """
    #return view_table("products_2_servdirs")
    return _view_request_results("servdirs2families", 
                                "select serv.name as service_directory ,\
                                 fam.name as 'family name',\
                                 fam.description as 'family description',\
                                 serv.servID as 'service ID',\
                                 fam.famID as 'family ID'\
                                 from service_dirs as serv, families as fam,\
                                 servdirs_2_families as serv2fam \
                                 where serv.servID = serv2fam.servID and fam.famID = serv2fam.famID")

@access.route('/tbl_servdirs_2_families')
def view_tbl_servdirs_2_families():
    """ 
       Viewer table servdirs_2_families
    """
    return _view_table("servdirs_2_families")
