# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_tempalte, flash

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

app.config.from_envar('FLASKR_SETTINGS', silent=True) #silent here just tells flask to not complain if the environment variable is not found.

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

