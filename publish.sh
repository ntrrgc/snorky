#!/bin/bash
set -eu

python2 -m unittest
python3 -m unittest

version=$(python -c 'import snorky; print(snorky.version)')
git tag -a "$version"
python3 setup.py register -r pypi
python3 setup.py sdist upload -r pypi
