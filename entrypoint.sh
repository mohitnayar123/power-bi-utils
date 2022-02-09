#!/bin/sh
pip install --upgrade pip
pip install requests
pip install pyyaml

python /scripts/python/upload_file.py --files "$1"
