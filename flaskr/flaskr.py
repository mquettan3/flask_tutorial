# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# The next few lines create the actual application instance and initialize it with the config from this same file.  However, a cleaner solution is to create a separate .ini or .py file, load that, and import the values from there.

app = Flask(__name__) # create the application instance
app.config.from_object(__name__) # load config from this file, flaskr.py

# Load the default config and override config from an environment variable

app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'flaskr.db'),
	SECRET_KEY='development key',
	USERNAME='admin',
	PASSWORD='default'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True) #silent here just tells flask to not complain if the environment variable is not found.

# Operating systems know the concept of the PWD for each process.  However, more than one application may run in a single process.  So we use app.root_path.  Together with the os.path module, files can be easily found.  For this example we place the database right next to the application.  For a real-world application, it's recommended to use Instance Folders instead.
# the SECRET_KEY here keeps the client/server connection secure.
# The config object works similarly to a dictionary, so it can be updated with new values.


# Method for easy connections to the specified database.  This can be used to open a connection on request and also from the interactive Python shell or a script.  Creates a simple database connection through SQLite and then tell it to use the sqlite3.Row object to represent rows.  This allows the rwos to be treated as if they were dictionaries isntead of tuples.
def connect_db():
	"""Connects to the specific database."""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	"""Opens a new database connection if there is none yet for the current application context."""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
		return g.sqlite_db

# Called every time the app context tears down.  App context is created before the request comes in and is destroyed (torn down) whenever the request finishes.
@app.teardown_appcontext
def close_db(error):
	"""Closes the database again at the end of the request."""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
		db.commit()

#The app.cli.command decorator registers a new command with the flask script.  When the command executes, Flask will automatically create an application context which is bound to the right application.  Within the function you can then access flask.g and other things as you might expect.  When the script ends, the application context tears down and the database connection is released.

#To run this, execute the following in bash:
#$flask initdb
@app.cli.command('initdb')
def initdb_command():
	"""Initializes the database."""
	init_db()
	print('Initialized the database.')

#Show entries in database
@app.route('/')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)

#Add new entry
#Note: Be sure to use question marks when building SQL statements.  Otherwise, using string formating will cause you to be sucuceptable to SQL injection.
@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries (title, text) values (?, ?)',
		[request.form['title'], request.form['text']])
	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)

#Logout
@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))

#Note:  Passwords should never be stored in plain text in a production system.  This tutorial uses plain text passwords for simplicity.  If you plan on storing passwords they should be both hashed and salted before being stored in a database or file.  Fortunately, there are flask extensions for this purpose so adding this functionality is fairly straigth forward.
