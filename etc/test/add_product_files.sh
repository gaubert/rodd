#!/bin/bash

# product service delete
prod_uid=$1
file_path=$2
if [[ -z $prod_uid || -z $file_path ]]
then
	# empty string
	echo "usage: ./add_product_files prod_uid json_file_description_filepath"
else
	value=`cat $file_path`
	curl "http://127.0.0.1:5000/product/$prod_uid/files" -X POST -i -H "Content-type: application/json" -d"$value" 
fi

