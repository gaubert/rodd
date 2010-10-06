#!/bin/bash

# product service delete
prods=$1
if [ -z $prods ]
then
	# empty string
	curl "http://127.0.0.1:5000/channels" -i -H "Content-type: application/json"
else
	curl "http://127.0.0.1:5000/channels/$prods" -i -H "Content-type: application/json"  
fi

