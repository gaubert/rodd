#!/bin/bash

fullfile=$1

filename=$(basename $fullfile)
extension=${filename##*.}
filename=${filename%.*}


#extract all dimensions except lat and lon
ncdump -v time,sea_surface_temperature,sst_dtime,SSES_bias_error,SSES_standard_deviation_error,satellite_zenith_angle,solar_zenith_angle,rejection_flag,confidence_flag,proximity_confidence,sea_ice_fraction,sources_of_sea_ice_fraction,wind_speed,sources_of_wind_speed,surface_solar_irradiance,ssi_dtime_from_sst,sources_of_ssi,DT_analysis $1 > $filename.cdl

