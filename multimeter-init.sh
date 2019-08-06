#!/usr/bin/bash
set -e
cd "$(dirname "$0")"
source ./env.sh

./check-updates.sh

python build.py init
python build.py deploy ./images/multimeter