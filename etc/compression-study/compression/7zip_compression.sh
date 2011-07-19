#!/bin/bash

input=$1
output=$2

#7za a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on $*
/homespace/gaubert/compressor/p7zip_9.13/bin/7za a $2 $1

