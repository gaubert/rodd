#!/bin/bash

NCGEN=/homespace/gaubert/Dev/c/inst/netcdf-4.1.1/bin/ncgen

cdl_file=$1
out_file=$2

$NCGEN -b -o $out_file $cdl_file
res=$?

exit $res