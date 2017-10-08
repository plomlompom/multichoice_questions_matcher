#!/bin/sh
set -e
set -x

python3 -m unittest matchlib.py
python3 -m unittest matcher.py

echo "Tests succeeded."
