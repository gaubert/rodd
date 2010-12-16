#!/bin/bash

# product service delete
prod_uid=$1
if [[ -z $prod_uid ]]
then
	# empty string
	echo "usage: ./get_file_product prod_uid"
else
	curl "http://127.0.0.1:5000/product/$prod_uid/files" -i -H "Content-type: application/json"  
fi

