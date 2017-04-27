#!/bin/bash
#This is an alternate way to create the database.  This will be done by the python init_db() function but could alternatively do here.
sqlite3 /tmp/flaskr.db < schema.sql
