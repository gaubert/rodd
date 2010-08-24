from bottle import route, run, template, send_file, debug
from eumetsat.db import connections

@route('/format_type')
def view_format_type():
    
    try:
        conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
        conn.connect()
    
        result = conn.execute("select * from format_type")
        
        output = template('format_type_table', rows=result)
        
        print("got output\n")

        return output

    except Exception,e:
        return e

@route('/products')
def view_products():
    
    try:
        conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
        conn.connect()
    
        result = conn.execute("select * from products")
        
        output = template('products_table', rows=result)
        
        print("got output\n")

        return output

    except Exception,e:
        return e

#route static files like (css, js, ...)
@route('/media/:filename#.*#')
def static_file(filename):
    send_file(filename, root='./media/')

    
    
   
#activate debug  
debug(True)

#activate reloader for debugging purposes
run(reloader=True, host='localhost', port=8080)

