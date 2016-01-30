#!/bin/bash
set -eu

if [ ! $(git diff --staged |wc -l) -eq 0 ]; then
  echo 'Commit changes first!'
  exit 1
fi

export PYTHONPATH="$PWD:$PYTHONPATH"
./doc/bump_version.py

python2 -m unittest discover snorky/tests
python3 -m unittest discover snorky/tests

version=$(python -c 'import snorky; print(snorky.version)')

git tag -a "v${version}" -F doc/releases/v${version}.rst
python3 setup.py register -r pypi
python3 setup.py sdist upload -r pypi
git push --tags

pushd ../snorky-web/source/
echo v${version} > version.txt
./generate.sh
popd
