#!/bin/bash

#read json file
value=`cat channel.txt`

#echo $value

# json echo service
curl "http://127.0.0.1:5000/channels" -i -H "Content-type: application/json" -X POST -d"$value"

