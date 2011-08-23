#!/bin/bash

# channel service delete
curl "http://127.0.0.1:5000/channels/$1" -i -H "Content-type: application/json" -X DELETE 

