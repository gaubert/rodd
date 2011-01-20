'''
Created on Sep 13, 2010

@author: guillaume.aubert@eumetsat.int
'''

from flask import g, Flask, render_template, request, redirect, flash, url_for, jsonify
from wtforms import Form, PasswordField, BooleanField, TextField, validators
import sqlalchemy

from eumetsat.common.logging_utils import LoggerFactory

from eumetsat.viewer.views.access import access
from eumetsat.viewer.views.json_access import json_access

from eumetsat.db.rodd_db import DAO


app = Flask(__name__)
app.register_module(access)
app.register_module(json_access)

@app.before_request
def before_request():
    """ before request method """
    g.dao = DAO()


class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


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
        
        users = sqlalchemy.Table('users', g.db_conn.get_metadata(), autoload=True)
        
        sql_request = sqlalchemy.select( [users.c.login, users.c.password] )\
                                .where( (users.c.login == request.form['username']) &  (users.c.password == request['form']) )
        
        result = g.db_conn.execute(sql_request)
        
        if result:
            flash('You were sucessfully logged in','error')
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials'
        
    return render_template('login.tpl', error=error)

#route index.html and default to product details page
@app.route('/')
@app.route('/index.html')
def index():
    #return redirect(url_for('access.view_channels'))
    return redirect(url_for('static', filename='index.html'))

@app.route('/add', methods=['POST'])
def add():
    #return unicode(request.json)
    return unicode("result =  %s\n" % (request.json['a'] + request.json['b']))
        
# set the secret key.  keep this really secret:
app.secret_key = '\x82*-\x975\xeb\xcb-c\xe3\x1d\xf7\x90~\x9e\xbf\x08g\xe7\xb0\xca\x1e\x130'

    

if __name__ == "__main__":
    app.run(debug=True)
