#!/bin/sh
pip install --upgrade pip
pip install requests
pip install pyyaml
pip install pandas
pip install json
pip install os

python /scripts/python/upload_file.py --files "$1"
