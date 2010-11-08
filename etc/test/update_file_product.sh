#!/bin/bash

# product service delete
prod_uid=$1
rodd_file_name=$2
file_path=$3
if [[ -z $prod_uid || -z $rodd_file_name || -z $file_path ]]
then
	# empty string
	echo "usage get_file_product prod_uid rodd_file_name json_file"
else
    value=`cat $3`
	curl "http://127.0.0.1:5000/product/$prod_uid/file/$rodd_file_name" -X PUT -i -H "Content-type: application/json" -d"$value"
fi

