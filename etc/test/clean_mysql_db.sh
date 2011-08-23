#!/bin/bash

cat /homespace/gaubert/Dev/projects/rodd/sql/create_light_rodd_mysql.sql | ssh tclxs30 "mysql -u root "

exit $?
