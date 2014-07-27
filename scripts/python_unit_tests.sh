#!/bin/bash

if [ $# -eq 0 ]; then
  PY_EXECUTABLE=python
elif [ $# -eq 1 ]; then
  PY_EXECUTABLE="$1"
else
  echo "Too many arguments."
  exit 1
fi

SNORKY="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"
export PYTHONPATH="${SNORKY}:${PYTHONPATH}"

cd "${SNORKY}"
exec ${PY_EXECUTABLE} -m unittest discover
