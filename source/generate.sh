#!/bin/bash
if [ ! -d env ]; then
  virtualenv -p $(which python3) env
  source ./env/bin/activate
  pip install -r requirements.txt
else
  source ./env/bin/activate
fi

python generate.py
