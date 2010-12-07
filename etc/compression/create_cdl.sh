#!/bin/bash

NCDUMP=/homespace/gaubert/Dev/c/inst/netcdf-4.1.1/bin/ncdump

in_file=$1
out_file=$2


#extract all dimensions except lat and lon
$NCDUMP -v time,sea_surface_temperature,sst_dtime,SSES_bias_error,SSES_standard_deviation_error,satellite_zenith_angle,solar_zenith_angle,rejection_flag,confidence_flag,proximity_confidence,sea_ice_fraction,sources_of_sea_ice_fraction,wind_speed,sources_of_wind_speed,surface_solar_irradiance,ssi_dtime_from_sst,sources_of_ssi,DT_analysis $in_file > $out_file
res=$?

exit $res
