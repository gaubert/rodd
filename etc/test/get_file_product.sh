#!/bin/bash

# product service delete
prod_uid=$1
file_name=$2
if [[ -z $prods && -z $file_name ]]
then
	# empty string
	echo "usage get_file_product prod_uid file_name"
else
	curl "http://127.0.0.1:5000/product/$prod_uid/file/$file_name" -i -H "Content-type: application/json"  
fi

