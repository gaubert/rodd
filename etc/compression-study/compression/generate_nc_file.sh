#!/bin/bash

NCGEN=/homespace/gaubert/Dev/c/inst/netcdf-4.1.1/bin/ncgen

cdl_file=$1
out_file=$2
#can be 3 or 4
netcdf_ver=$3

# -k 4 to generate a netcdf4 type
$NCGEN -k $3 -b -o $out_file $cdl_file
res=$?

exit $res