'''
Created on Sep 13, 2010

@author: guillaume.aubert@eumetsat.int
'''

from flask import g, Flask, render_template, request, redirect, flash, url_for, jsonify
from wtforms import Form, PasswordField, BooleanField, TextField, validators
import sqlalchemy

from eumetsat.db import connections
from eumetsat.common.logging_utils import LoggerFactory

from eumetsat.viewer.views.access import access


app = Flask(__name__)
app.register_module(access)

@app.before_request
def before_request():
    
    conn = connections.DatabaseConnector("mysql://rodd:ddor@tclxs30/RODD")
    
    conn.connect()
    
    g.db_conn = conn

@app.after_request
def after_request(response):
    g.db_conn.disconnect()
    return response


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/count_numbers')
def _add_numbers():
    app.logger.info("Hello numbers")
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)


@app.route('/add_numbers')
def add_numbers():
    return render_template('numbers.tpl')



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        
        username = form.username.data
        email    = form.email.data
        password = form.password.data
        
        users = sqlalchemy.Table('users', g.db_conn.get_metadata(), autoload=True)

        g.db_conn.execute(users.insert().values(useID=None, login=username, password=password, email=email))
        
        flash('Thanks for registering (%s,%s)' % (username, email))
        return redirect(url_for('login'))
    
    return render_template('register.tpl', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
           request.form['password'] != 'secret':
            error = 'Invalid credentials'
        else:
            flash('You were sucessfully logged in','error')
            return redirect(url_for('index'))
    return render_template('login.tpl', error=error)

#route index.html and default to product details page
@app.route('/')
@app.route('/index.html')
def index():
    return view_products_details()

@app.route("/hello")
def hello():
    return "Hello World!"




# set the secret key.  keep this really secret:
app.secret_key = '\x82*-\x975\xeb\xcb-c\xe3\x1d\xf7\x90~\x9e\xbf\x08g\xe7\xb0\xca\x1e\x130'

    

if __name__ == "__main__":
    app.run(debug=True)
