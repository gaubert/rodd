#!/bin/bash

input=$1
output=$2

bzip2 -c $input > $output
