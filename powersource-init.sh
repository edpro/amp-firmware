#!/usr/bin/bash
set -e
cd "$(dirname "$0")" && source ./env.sh

python build.py init
python build.py deploy ./powersource