#!/bin/bash

#read json file
file_name=$1

if [[ ! -e $file_name ]]
then
	# empty string
	echo "usage: ./add_channels.sh filename
	
parameters:
        filename: file containing the product details in json.	
	"
else

value=`cat $file_name`
# json echo service
curl "http://127.0.0.1:5000/channels" -i -H "Content-type: application/json" -X POST -d"$value"

fi

