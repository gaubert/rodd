#!/bin/bash

#rm -f /homespace/gaubert/mydb
sqlite3 /homespace/gaubert/mydb < /homespace/gaubert/ecli-workspace/rodd/sql/create_light_rodd_sqlite3.sql 

exit $?
