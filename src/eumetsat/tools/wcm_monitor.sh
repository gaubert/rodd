#!/bin/bash

src_dir=/export/home/ipps/wcm_monitor

#dos2unix wcm_monitor.py to avoid any character issues (developed on Windows)
dos2unix "$src_dir/wcm_monitor.py"

nohup python -u "$src_dir/wcm_monitor.py" > wcm_monitor.log 2>&1 &
echo "Started wcm_monitor.py with nohup"
