from bottle import route, run, template, send_file, debug
from eumetsat.db import connections
from eumetsat.readers.csv_light_rodd_extractor import LCSVRoddExtractor


def view_table(a_table_name):
    """
       Return the content of the sql table provided its name
    """
    try:
        conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
        conn.connect()
        
        # get metadata to get the columns names
        metadata = conn.getTableMetadata(a_table_name)
        
        col_names = [ dic["name"] for dic in metadata ]
    
        result = conn.execute("select * from %s" % (a_table_name) )
        
        output = template('generic_table', rows = result, heads = col_names, table= a_table_name)
        
        print("got output\n")
    
        return output
    
    except Exception, the_exc:
        return the_exc

def view_request_results(a_request_name, a_sql_req):
    
    """
       Return the content of the sql request provided its name
    """
    try:
        conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
        conn.connect()
        
        # get metadata to get the columns names
        #metadata = conn.getTableMetadata(a_table_name)
        
        #col_names = [ dic["name"] for dic in metadata ]
    
        result = conn.execute(a_sql_req)
        
        cols = result.fetchall()
        
        #return "dir(cols[0]) =%s\n" %( dir(result) )
        #return "dir(cols[0]) =%s\n" %( cols[0].keys() )
        
        cols_names = cols[0].keys()
        
        output = template('generic_table', rows = cols, heads = cols_names, table= a_request_name)
        
        print("got output\n")
    
        return output
    
    except Exception, the_exc:
        return the_exc

@route('/format_type')
def view_format_type():
    """ 
       Viewer for format_type 
    """
    return view_table("format_type")

@route('/products')
def view_products():
    """ 
       Viewer for products 
    """
    return view_table("products")
    

@route('/channels')
def view_channels():
    """ 
       Viewer for channels 
    """
    return view_table("channels")

@route('/service_dirs')
def view_services():
    """ 
       Viewer for service_dirs 
    """
    return view_table("service_dirs")

@route('/products_2_servdirs')
def view_products_2_servdirs():
    """ 
       Viewer for products_2_servdirs 
    """
    #return view_table("products_2_servdirs")
    return view_request_results("products2service", "select products.title as 'Product Name', service_dirs.name as 'Service Dir Name', products.roddID as 'roddID', service_dirs.servID as 'servID' from products, service_dirs, products_2_servdirs as p2s where p2s.roddID=products.roddID and p2s.servID=service_dirs.servID")

@route('/tbl_prod2servdirs')
def view_tbl_prod2servdirs():
    """ 
       Viewer table prod2servdirs
    """
    return view_table("products_2_servdirs")

#route static files like (css, js, ...)
@route('/media/:filename#.*#')
def static_file(filename):
    """ 
       Route to access all the static files in media 
    """
    send_file(filename, root='./media/')

    
    
   
#activate debug  
debug(True)

#activate reloader for debugging purposes
run(reloader=True, host='localhost', port=8080)



