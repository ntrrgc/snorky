#!/bin/bash
if [ ! -d env ]; then
  virtualenv -p $(which python3.4) env
  source ./env/bin/activate
  pip install -r requirements.txt
else
  source ./env/bin/activate
fi

python generate.py && git add ../index.html && git commit -m 'Build' && git push
