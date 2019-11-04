#!/usr/bin/bash
cd "$(dirname "$0")" || exit 1
source ./env.sh
./update.sh
python tools/accum_test.py || read -rp "Error has occured..."
