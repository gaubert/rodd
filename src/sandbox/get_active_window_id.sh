#!/bin/bash

xprop -root | grep "_NET_ACTIVE_WINDOW(WINDOW)" | awk '{print $5}'
