#!/bin/bash

# product service delete
prod_uid=$1
file_name=$2
if [[ -z $prod_uid || -z $file_name ]]
then
	# empty string
	echo "usage: ./delete_product_files prod_uid file_name"
else
	curl "http://127.0.0.1:5000/product/$prod_uid/files/$file_name" -X DELETE -i -H "Content-type: application/json" 
fi

