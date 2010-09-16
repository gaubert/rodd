from bottle import route, run, template, send_file, debug, request

from wtforms import Form, BooleanField, TextField, validators

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
    
class RegistrationForm(Form):
    username     = TextField('MyName', [validators.Length(min=4, max=25)])
    email        = TextField('Email Address', [validators.Length(min=6, max=35)])
    accept_rules = BooleanField('I accept the site rules', [validators.Required()])


@route("/login", method="GET")
def view_login():
    return template("login", form=RegistrationForm()) 

@route("/login", method="POST")
def post_login():   
    return template("login", form=RegistrationForm())

@route('/format_type')
def view_format_type():
    """ 
       Viewer for format_type 
    """
    return view_table("format_type")

@route('/tbl_products')
def view_tbl_products():
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

@route('/families')
def view_families():
    """ 
       Viewer for families 
    """
    return view_table("families")

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
    return view_request_results("products2service", 
                                "select products.title as 'Product Name', \
                                service_dirs.name as 'Service Dir Name', \
                                products.roddID as 'roddID', \
                                service_dirs.servID as 'servID' \
                                from products, service_dirs, products_2_servdirs as p2s \
                                where p2s.roddID=products.roddID and p2s.servID=service_dirs.servID")
    
@route('/products_details')
def view_products_details():
    """ 
       Viewer for products_details 
    """
    #return view_table("products_2_servdirs")
    return view_request_results("products details", 
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
       

@route('/tbl_products_2_servdirs')
def view_tbl_products_2_servdirs():
    """ 
       Viewer table prod2servdirs
    """
    return view_table("products_2_servdirs")

@route('/servdirs_2_families')
def view_servdirs_2_families():
    """ 
       Viewer for servdirs_2_families 
    """
    #return view_table("products_2_servdirs")
    return view_request_results("servdirs2families", 
                                "select serv.name as service_directory ,\
                                 fam.name as 'family name',\
                                 fam.description as 'family description',\
                                 serv.servID as 'service ID',\
                                 fam.famID as 'family ID'\
                                 from service_dirs as serv, families as fam,\
                                 servdirs_2_families as serv2fam \
                                 where serv.servID = serv2fam.servID and fam.famID = serv2fam.famID")

@route('/tbl_servdirs_2_families')
def view_tbl_servdirs_2_families():
    """ 
       Viewer table servdirs_2_families
    """
    return view_table("servdirs_2_families")


#route index.html and default to product details page
@route('/')
@route('/index.html')
def index():
    return view_products_details()



#route static files like (css, js, ...)
@route('/static/:filename#.*#')
def static_file(filename):
    """ 
       Route to access all the static files in media 
    """
    send_file(filename, root='./static/')

    
    
   
#activate debug  
debug(True)

#activate reloader for debugging purposes
run(reloader=True, host='localhost', port=8080)



