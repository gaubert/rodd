#!/bin/bash

#######
# add import pdb; pdb.set_trace() to add a break point in your code
#######
export PYTHONPATH=/homespace/gaubert/ecli-workspace/rodd/src:/homespace/gaubert/ecli-workspace/rodd/conf-src;$PYTHONPATH

python /homespace/gaubert/ecli-workspace/rodd/src/eumetsat/viewer/flask_server.py

