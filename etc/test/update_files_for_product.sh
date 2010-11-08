#!/bin/bash

# product service delete
prod_uid=$1
diss_type=$2
value_file_path=$3
if [[ -z $prod_uid || -z $diss_type || -z $value_file_path ]]
then
	# empty string
	echo "usage update_files_for_product prod_uid diss_type value_file_path"
else
    value=`cat $value_file_path`
	curl "http://127.0.0.1:5000/product/$prod_uid/files/$diss_type" -X PUT -i -H "Content-type: application/json" -d"$value"
fi

