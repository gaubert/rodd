#!/bin/bash

# product service delete
curl "http://127.0.0.1:5000/products/$1" -i -H "Content-type: application/json" -X DELETE 

