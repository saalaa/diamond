#!/bin/sh -e

rm -rf diamond_wiki.egg-info

rm -rf build

rm -rf __pycache__

find tests -name '__pycache__' -exec rm -rf '{}' \;
find diamond -name '__pycache__' -exec rm -rf '{}' \;
find migrations -name '__pycache__' -exec rm -rf '{}' \;

find tests -name '*.pyc' -exec rm -f '{}' \;
find diamond -name '*.pyc' -exec rm -f '{}' \;
find migrations -name '*.pyc' -exec rm -f '{}' \;
