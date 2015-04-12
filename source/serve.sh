#!/bin/bash
if [ ! -d env ]; then
  virtualenv -p $(which python3) env
  source ./env/bin/activate
  pip install -r requirements.txt
else
  source ./env/bin/activate
fi

RUN_LOCAL=1 python manage.py runserver 0.0.0.0:8000
