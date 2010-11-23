#!/bin/bash

#rm -f /homespace/gaubert/mydb
sqlite3 /homespace/gaubert/mydb < /homespace/gaubert/Dev/projects/rodd/sql/create_light_rodd_sqlite3.sql 

exit $?
