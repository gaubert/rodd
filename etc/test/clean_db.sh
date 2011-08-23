#!/bin/bash

#rm -f /homespace/gaubert/mydb
sqlite3 /homespace/gaubert/mydb < /homespace/gaubert/ecli-workspace/rodd/sql/clean_database.sql

exit $?
